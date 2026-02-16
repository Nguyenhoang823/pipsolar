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

# ================== 24V MODEL ==================
CONF_BATTERY_BULK_VOLTAGE = "battery_bulk_voltage"
CONF_BATTERY_RECHARGE_VOLTAGE = "battery_recharge_voltage"
CONF_BATTERY_UNDER_VOLTAGE = "battery_under_voltage"
CONF_BATTERY_FLOAT_VOLTAGE = "battery_float_voltage"
CONF_BATTERY_REDISCHARGE_VOLTAGE = "battery_redischarge_voltage"

TYPES = {
    CONF_BATTERY_BULK_VOLTAGE: (
        [26.0, 26.5, 27.0, 27.5, 28.0, 28.5, 29.0],
        "PCVV%.1f",
    ),

    CONF_BATTERY_RECHARGE_VOLTAGE: (
        [22.0, 22.5, 23.0, 23.5, 24.0, 24.5, 25.0, 25.5],
        "PBCV%.1f",
    ),

    CONF_BATTERY_UNDER_VOLTAGE: (
        [20.0, 21.0, 22.0, 23.0, 24.0],
        "PSDV%.1f",
    ),

    CONF_BATTERY_FLOAT_VOLTAGE: (
        [26.0, 26.5, 27.0, 27.5],
        "PBFT%.1f",
    ),

    CONF_BATTERY_REDISCHARGE_VOLTAGE: (
        [24.0, 24.5, 25.0, 25.5, 26.0, 26.5, 27.0, 27.5, 28.0, 28.5, 29.0],
        "PBDV%.1f",
    ),
}

CONFIG_SCHEMA = PIPSOLAR_COMPONENT_SCHEMA.extend(
    {
        cv.Optional(type): output.FLOAT_OUTPUT_SCHEMA.extend(
            {
                cv.Required(CONF_ID): cv.declare_id(PipsolarOutput),
            }
        )
        for type in TYPES
    }
)


async def to_code(config):
    parent = await cg.get_variable(config[CONF_PIPSOLAR_ID])

    for type, (values, command) in TYPES.items():
        if type in config:
            conf = config[type]
            var = cg.new_Pvariable(conf[CONF_ID])
            await output.register_output(var, conf)

            cg.add(var.set_parent(parent))
            cg.add(var.set_set_command(command))
            cg.add(var.set_possible_values(values))


# ================== ACTION ==================
@automation.register_action(
    "output.pipsolar.set_level",
    SetOutputAction,
    cv.Schema(
        {
            cv.Required(CONF_ID): cv.use_id(PipsolarOutput),
            cv.Required(CONF_VALUE): cv.templatable(cv.positive_float),
        }
    ),
)
async def output_pipsolar_set_level_to_code(config, action_id, template_arg, args):
    parent = await cg.get_variable(config[CONF_ID])
    var = cg.new_Pvariable(action_id, template_arg, parent)
    template_ = await cg.templatable(config[CONF_VALUE], args, float)
    cg.add(var.set_level(template_))
    return var
