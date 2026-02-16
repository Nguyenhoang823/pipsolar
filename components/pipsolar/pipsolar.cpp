#include "pipsolar.h"
#include "pipsolar_component.h"

namespace esphome {
namespace pipsolar {

void PipsolarOutput::write_state(float state) {
  if (this->parent_ == nullptr)
    return;

  char buffer[24];
  snprintf(buffer, sizeof(buffer), this->command_.c_str(), state);

  this->parent_->send_command_(buffer);
}

}  // namespace pipsolar
}  // namespace esphome
