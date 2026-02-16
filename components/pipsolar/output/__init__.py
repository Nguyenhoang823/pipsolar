import esphome.codegen as cg
import esphome.config_validation as cv
from esphome import automation
from esphome.components import output
from esphome.const import CONF_ID, CONF_VALUE

from .. import CONF_PIPSOLAR_ID, PIPSOLAR_COMPONENT_SCHEMA, pipsolar_ns

DEPENDENCIES = ["pipsolar"]

PipsolarOutput = pipsolar_ns.class_("PipsolarOutput", output.FloatOutput)
SetOutputAction = pipsolar_ns.class_("SetOutputAction", automation.Action)

CONF_POSSIBLE_VALUES = "possible_values"

# =========================================================
# PIPSOLAR / EASUN – HỆ 24V
#
# battery_bulk_voltage;          26.0V ~ 29.0V
# battery_recharge_voltage;      22.0V ~ 25.5V
# battery_under_voltage;         20.0V ~ 24.0V
# battery_float_voltage;         26.0V ~ 27.5V
# battery_redischarge_voltage;   24.0V ~ 29.0V
#
# ⚠️ P04 = USE (USER)
# =========================================================

CONF_BATTERY_BULK_VOLTAGE = "battery_bulk_voltage"
CONF_BATTERY_RECHARGE_VOLTAGE = "battery_recharge_voltage"
CONF_BATTERY_UNDER_VOLTAGE = "battery_under_voltage"
CONF_BATTERY_FLOAT_VOLTAGE = "battery_float_voltage"
CONF_BATTERY_TYPE = "battery_type"
CONF_CURRENT_MAX_AC_CHARGING_CURRENT = "current_max_ac_charging_current"
CONF_CURRENT_MAX_CHARGING_CURRENT = "current_max_charging_current"
CONF_OUTPUT_SOURCE_PRIORITY = "output_source_priority"
CONF_CHARGER_SOURCE_PRIORITY = "charger_source_priority"
CONF_BATTERY_REDISCHARGE_VOLTAGE = "battery_redischarge_voltage"

# ================== DẢI GIÁ TRỊ HỆ 24V ==================
TYPES = {
    CONF_BATTERY_BULK_VOLTAGE: (
        [26.0, 26.5, 27.0, 27.5, 28.0, 28.5, 29.0],
        "PCVV%02.1f",
    ),

    CONF_BATTERY_RECHARGE_VOLTAGE: (
        [22.0, 22.5, 23.0, 23.5, 24.0, 24.5, 25.0, 25.5],
        "PBCV%02.1f",
    ),

    CONF_BATTERY_UNDER_VOLTAGE: (
        [20.0, 21.0, 22.0, 23.0, 24.0],
        "PSDV%02.1f",
    ),

    CONF_BATTERY_FLOAT_VOLTAGE: (
        [26.0, 26.5, 27.0, 27.5],
        "PBFT%02.1f",
    ),

    CONF_BATTERY_TYPE: (
        [0, 1, 2],   # AGM / Flooded / USE (tùy model)
        "PBT%02.0f",
    ),

    CONF_CURRENT_MAX_AC_CHARGING_CURRENT: (
        [10, 20, 30, 40, 50],
        "MUCHGC%04.0f",
    ),

    CONF_CURRENT_MAX_CHARGING_CURRENT: (
        [10, 20, 30, 40, 50],
        "MNCHGC0%03.0f",
    ),

    CONF_OUTPUT_SOURCE_PRIORITY: (
        [0, 1, 2],   # USB / SUB / SBU
        "POP%02.0f",
    ),

    CONF_CHARGER_SOURCE_PRIORITY: (
        [0, 1, 2, 3],
        "PCP%02.0f",
    ),

    CONF_BATTERY_REDISCHARGE_VOLTAGE: (
        [24.0, 24.5, 25.0, 25.5, 26.0, 26.5, 27.0, 27.5, 28.0, 28.5, 29.0],
        "PBDV%02.1f",
    ),
}

# ================== CONFIG SCHEMA ==================
CONFIG_SCHEMA = PIPSOLAR_COMPONENT_SCHEMA.extend(
    {
        cv.Optional(type): output.FLOAT_OUTPUT_SCHEMA.extend(
            {
                cv.Required(CONF_ID): cv.declare_id(PipsolarOutput),
                cv.Optional(CONF_POSSIBLE_VALUES, default=values): cv.All(
                    cv.ensure_list(cv.positive_float),
                    cv.Length(min=1),
                ),
            }
        )
        for type, (values, _) in TYPES.items()
    }
)

# ================== CODEGEN ==================
async def to_code(config):
    parent = await cg.get_variable(config[CONF_PIPSOLAR_ID])

    for type, (_, command) in TYPES.items():
        if type in config:
            conf = config[type]
            var = cg.new_Pvariable(conf[CONF_ID])
            await output.register_output(var, conf)
            cg.add(var.set_parent(parent))
            cg.add(var.set_set_command(command))
            if CONF_POSSIBLE_VALUES in conf:
                cg.add(var.set_possible_values(conf[CONF_POSSIBLE_VALUES]))


# ================== AUTOMATION ACTION ==================
@automation.register_action(
    "output.pipsolar.set_level",
    SetOutputAction,
    cv.Schema(
        {
            cv.Required(CONF_ID): cv.use_id(CONF_ID),
            cv.Required(CONF_VALUE): cv.templatable(cv.positive_float),
        }
    ),
)
def output_pipsolar_set_level_to_code(config, action_id, template_arg, args):
    parent = yield cg.get_variable(config[CONF_ID])
    var = cg.new_Pvariable(action_id, template_arg, parent)
    template_ = yield cg.templatable(config[CONF_VALUE], args, float)
    cg.add(var.set_level(template_))
    yield var