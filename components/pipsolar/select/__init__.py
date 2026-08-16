import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import select
from esphome.const import CONF_ID, CONF_OPTIMISTIC, CONF_ENTITY_CATEGORY

from .. import CONF_PIPSOLAR_ID, PIPSOLAR_COMPONENT_SCHEMA, pipsolar_ns

DEPENDENCIES = ["uart"]

CODEOWNERS = ["@andreashergert1984"]
CONF_OPTIONSMAP = "optionsmap"
CONF_STATUSMAP = "statusmap"

CONF_OUTPUT_SOURCE_PRIORITY = "output_source_priority"
CONF_CHARGER_SOURCE_PRIORITY = "charger_source_priority"
CONF_CHARGING_DISCHARGING_CONTROL = "charging_discharging_control"
CONF_CURRENT_MAX_CHARGING_CURRENT = "current_max_charging_current"
CONF_CURRENT_MAX_AC_CHARGING_CURRENT = "current_max_ac_charging_current"

CONF_BATTERY_BULK_VOLTAGE_SELECT = "battery_bulk_voltage_select"
CONF_BATTERY_RECHARGE_VOLTAGE_SELECT = "battery_recharge_voltage_select"
CONF_BATTERY_UNDER_VOLTAGE_SELECT = "battery_under_voltage_select"
CONF_BATTERY_FLOAT_VOLTAGE_SELECT = "battery_float_voltage_select"
CONF_BATTERY_REDISCHARGE_VOLTAGE_SELECT = "battery_redischarge_voltage_select"


PipsolarSelect = pipsolar_ns.class_("PipsolarSelect", cg.Component, select.Select)


def ensure_option_map():
    def validator(value):
        cv.check_not_templatable(value)
        option = cv.All(cv.string_strict)
        mapping = cv.All(cv.string_strict)
        options_map_schema = cv.Schema({option: mapping})
        value = options_map_schema(value)

        all_values = list(value.values())
        unique_values = set(value.values())
        if len(all_values) != len(unique_values):
            raise cv.Invalid("Mapping values must be unique.")

        return value

    return validator


# def register_count_value_type_min(value):
#     reg_count = value.get(CONF_REGISTER_COUNT)
#     if reg_count is not None:
#         value_type = value[CONF_VALUE_TYPE]
#         min_register_count = TYPE_REGISTER_MAP[value_type]
#         if min_register_count > reg_count:
#             raise cv.Invalid(
#                 f"Value type {value_type} needs at least {min_register_count} registers"
#             )
#     return value

# INTEGER_SENSOR_VALUE_TYPE = {
#     key: value for key, value in SENSOR_VALUE_TYPE.items() if not key.startswith("FP")
# }

# CONFIG_SCHEMA = cv.All(
#     select.SELECT_SCHEMA.extend(cv.COMPONENT_SCHEMA).extend(
#         {
#             cv.GenerateID(): cv.declare_id(PipSolarSelect),
#             cv.GenerateID(CONF_MODBUS_CONTROLLER_ID): cv.use_id(ModbusController),
#             cv.Required(CONF_ADDRESS): cv.positive_int,
#             cv.Optional(CONF_VALUE_TYPE, default="U_WORD"): cv.enum(
#                 INTEGER_SENSOR_VALUE_TYPE
#             ),
#             cv.Optional(CONF_REGISTER_COUNT): cv.positive_int,
#             cv.Optional(CONF_SKIP_UPDATES, default=0): cv.positive_int,
#             cv.Optional(CONF_FORCE_NEW_RANGE, default=False): cv.boolean,
#             cv.Required(CONF_OPTIONSMAP): ensure_option_map(),
#             cv.Optional(CONF_USE_WRITE_MULTIPLE, default=False): cv.boolean,
#             cv.Optional(CONF_OPTIMISTIC, default=False): cv.boolean,
#             cv.Optional(CONF_LAMBDA): cv.returning_lambda,
#             cv.Optional(CONF_WRITE_LAMBDA): cv.returning_lambda,
#         },
#     ),
#     register_count_value_type_min,
# )

TYPES = {
    CONF_OUTPUT_SOURCE_PRIORITY: ("POP00", None),
    CONF_CHARGER_SOURCE_PRIORITY: ("PCP03", None),
    CONF_CHARGING_DISCHARGING_CONTROL: ("PBATCD111", None),
    CONF_CURRENT_MAX_CHARGING_CURRENT: ("MCHGC010", None),
    CONF_CURRENT_MAX_AC_CHARGING_CURRENT: ("MUCHGC0002", None),
}

# Voltage dropdowns for 24 V inverters.
# key: (PIP command prefix, minimum, maximum, step)
VOLTAGE_TYPES = {
    CONF_BATTERY_BULK_VOLTAGE_SELECT: ("PCVV", 24.0, 29.2, 0.1),
    CONF_BATTERY_RECHARGE_VOLTAGE_SELECT: ("PBCV", 22.0, 25.5, 0.5),
    CONF_BATTERY_UNDER_VOLTAGE_SELECT: ("PSDV", 20.0, 24.0, 0.1),
    CONF_BATTERY_FLOAT_VOLTAGE_SELECT: ("PBFT", 24.0, 29.2, 0.1),
    CONF_BATTERY_REDISCHARGE_VOLTAGE_SELECT: ("PBDV", 24.0, 29.0, 0.5),
}


PIPSELECT_SCHEMA = (
    select.select_schema(PipsolarSelect)
    .extend(
        {
        cv.GenerateID(): cv.declare_id(PipsolarSelect),
        cv.Optional(CONF_OPTIONSMAP, default={}): ensure_option_map(),
        cv.Optional(CONF_STATUSMAP): ensure_option_map(),
    }
    )
    .extend(cv.COMPONENT_SCHEMA)
)

_UNDEF = object()


def select_schema(
    entity_category: str = _UNDEF,
):
    schema = cv.Schema({})
    if entity_category is not _UNDEF:
        schema = schema.extend(
            {
                cv.Optional(
                    CONF_ENTITY_CATEGORY, default=entity_category
                ): cv.entity_category
            }
        )

CONFIG_SCHEMA = PIPSOLAR_COMPONENT_SCHEMA.extend(
    {cv.Optional(type): PIPSELECT_SCHEMA for type in TYPES}
).extend(
    {cv.Optional(type): PIPSELECT_SCHEMA for type in VOLTAGE_TYPES}
)


async def to_code(config):
    paren = await cg.get_variable(config[CONF_PIPSOLAR_ID])

    for type, (on, off) in TYPES.items():
        if type in config:
            conf = config[type]
            options_map = conf[CONF_OPTIONSMAP]
            var = cg.new_Pvariable(conf[CONF_ID])
            await cg.register_component(var, conf)
            await select.register_select(var, conf, options=list(options_map.keys()))
            cg.add(getattr(paren, f"set_{type}_select")(var))
            cg.add(var.set_parent(paren))
            for mappingkey in options_map.keys():
                cg.add(var.add_mapping(mappingkey, options_map[mappingkey]))
            if CONF_STATUSMAP in conf:
                status_map = conf[CONF_STATUSMAP]
                for mappingkey in status_map.keys():
                    cg.add(var.add_status_mapping(mappingkey, status_map[mappingkey]))

    # Generate fixed 24 V voltage options automatically. Each displayed option
    # is e.g. "27.1 V", while the command sent to the inverter is "PCVV27.1".
    for type, (prefix, minimum, maximum, step) in VOLTAGE_TYPES.items():
        if type not in config:
            continue
        conf = config[type]
        generated = {}
        status_map = {}
        count = int(round((maximum - minimum) / step))
        for index in range(count + 1):
            value = minimum + index * step
            value_text = f"{value:.1f}"
            label = f"{value_text} V"
            generated[label] = f"{prefix}{value_text}"
            status_map[value_text] = label

        var = cg.new_Pvariable(conf[CONF_ID])
        await cg.register_component(var, conf)
        await select.register_select(var, conf, options=list(generated.keys()))
        # VOLTAGE_TYPES keys already end in "_select"; the C++ setter is
        # therefore set_<type>, not set_<type>_select.
        cg.add(getattr(paren, f"set_{type}")(var))
        cg.add(var.set_parent(paren))
        for label, command in generated.items():
            cg.add(var.add_mapping(label, command))
        for raw_value, label in status_map.items():
            cg.add(var.add_status_mapping(raw_value, label))


# async def to_code(config):
#     value_type = config[CONF_VALUE_TYPE]
#     reg_count = config.get(CONF_REGISTER_COUNT)
#     if reg_count is None:
#         reg_count = TYPE_REGISTER_MAP[value_type]

#     options_map = config[CONF_OPTIONSMAP]

#     var = cg.new_Pvariable(
#         config[CONF_ID],
#         value_type,
#         config[CONF_ADDRESS],
#         reg_count,
#         config[CONF_SKIP_UPDATES],
#         config[CONF_FORCE_NEW_RANGE],
#         list(options_map.values()),
#     )

#     await cg.register_component(var, config)
#     await select.register_select(var, config, options=list(options_map.keys()))

#     parent = await cg.get_variable(config[CONF_MODBUS_CONTROLLER_ID])
#     cg.add(parent.add_sensor_item(var))
#     cg.add(var.set_parent(parent))
#     cg.add(var.set_use_write_mutiple(config[CONF_USE_WRITE_MULTIPLE]))
#     cg.add(var.set_optimistic(config[CONF_OPTIMISTIC]))

#     if CONF_LAMBDA in config:
#         template_ = await cg.process_lambda(
#             config[CONF_LAMBDA],
#             [
#                 (ModbusSelect.operator("const_ptr"), "item"),
#                 (cg.int64, "x"),
#                 (
#                     cg.std_vector.template(cg.uint8).operator("const").operator("ref"),
#                     "data",
#                 ),
#             ],
#             return_type=cg.optional.template(cg.std_string),
#         )
#         cg.add(var.set_template(template_))

#     if CONF_WRITE_LAMBDA in config:
#         template_ = await cg.process_lambda(
#             config[CONF_WRITE_LAMBDA],
#             [
#                 (ModbusSelect.operator("const_ptr"), "item"),
#                 (cg.std_string.operator("const").operator("ref"), "x"),
#                 (cg.int64, "value"),
#                 (cg.std_vector.template(cg.uint16).operator("ref"), "payload"),
#             ],
#             return_type=cg.optional.template(cg.int64),
#         )
#         cg.add(var.set_write_template(template_))
