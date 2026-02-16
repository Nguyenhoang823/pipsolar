#pragma once

#include "esphome/core/component.h"
#include "esphome/components/output/float_output.h"

namespace esphome {
namespace pipsolar {

class PipsolarComponent;

class PipsolarOutput : public output::FloatOutput {
 public:
  void set_parent(PipsolarComponent *parent) { this->parent_ = parent; }
  void set_set_command(const std::string &command) { this->command_ = command; }
  void set_possible_values(const std::vector<float> &values) { this->possible_values_ = values; }

 protected:
  PipsolarComponent *parent_{nullptr};
  std::string command_;
  std::vector<float> possible_values_;

  void write_state(float state) override;
};

}  // namespace pipsolar
}  // namespace esphome
