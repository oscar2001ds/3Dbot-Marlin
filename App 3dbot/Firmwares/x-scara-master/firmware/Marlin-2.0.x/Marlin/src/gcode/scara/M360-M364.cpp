/**
 * Marlin 3D Printer Firmware
 * Copyright (c) 2020 MarlinFirmware [https://github.com/MarlinFirmware/Marlin]
 *
 * Based on Sprinter and grbl.
 * Copyright (c) 2011 Camiel Gubbels / Erik van der Zalm
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 */

#include "../../inc/MarlinConfig.h"

#if ENABLED(MORGAN_SCARA) 
#include "../gcode.h"
#include "../../module/scara.h"
#include "../../module/motion.h"
#include "../../MarlinCore.h" // for IsRunning()

  // TODO: fix morgan scara
#elif ENABLED(X_SCARA)

#include "../gcode.h"
#include "../../module/scara.h"
#include "../../module/motion.h"
#include "../../module/planner.h"
#include "../../MarlinCore.h" // for isRunning

FORCE_INLINE static bool _check_if_running() {
  if (!IsRunning()) {
    SERIAL_ECHOLNPGM("X-Scara is not running!");
    return true;
  }
  return false;
}
/**
 * M360: X-SCARA change coordinates transformation
 *
 * Parameters:
 *
 * M<int>  - transformation mode (0 or 1)
 * 
 *            0 - cartesian (default) 
 *                X and Y are cartesian coordinates
 * 
 *            1 - angular (just for testing and calibration) 
 *                X and Y are shoulder and elbow angles respectively)
 * 
 *            2 - probe (for G29) 
 *                X and Y point to probe's center (not nozzle)
 */
void GcodeSuite::M360() {
  
  // get mode from arguments
  if (parser.seenval('M')) {
    if (_check_if_running()) return;
    x_scara_change_coordinates_mode(parser.value_byte());
  }

  SERIAL_ECHOLNPAIR("Mode: ", x_scara_coordinates_mode, 
    " (",x_scara_coordinates_mode_str[x_scara_coordinates_mode], ")");
}

/*
 * M361: X-SCARA Move - Move joints to position
 *
 * Parameters:
 *
 * S<ang>  - Move to given shoulder angle
 * E<ang>  - Move to given elbow angle 
 * I<booL> - Add the given angles to current position instead of setting them
 */

void GcodeSuite::M361() {

  bool incr = false;
  
  ab_pos_t cur_pos = {
      planner.get_axis_position_degrees(A_AXIS),
      planner.get_axis_position_degrees(B_AXIS)
    };

  x_scara_delta_to_relative(cur_pos);
  ab_pos_t pos = cur_pos;

  // modifier to increment position
  if (parser.seenval('I')) incr = parser.value_bool();

  // shouler and elbow positions
  if (parser.seenval('S')) {
    pos.a = parser.value_float();
    if (incr) pos.a += cur_pos.a;
  }
  if (parser.seenval('E')) {
    pos.b = parser.value_float();
    if (incr) pos.b += cur_pos.b;
  }

  // do nothing if same position given
  if (cur_pos != pos)
  {
      if (_check_if_running()) return;
      x_scara_move_joints(pos);
  }
  
  SERIAL_ECHOLNPAIR(
    "S:", pos.a,
    " E:", pos.b, 
    " X:", current_position.x, 
    " Y:", current_position.y);
  return;
}

/**
 * M362: X-SCARA geometry : set current joints position
 *
 * Parameters:
 *
 * S<float>  - current shoulder angle
 * E<float>  - current elbow angle
 */
void GcodeSuite::M362() {

  // get current position from steppers
  ab_pos_t cur_pos = {
      planner.get_axis_position_degrees(A_AXIS),
      planner.get_axis_position_degrees(B_AXIS)
    };

  // convert stepper angles to joint angles
  x_scara_delta_to_relative(cur_pos);

  ab_pos_t pos = cur_pos;

  // overwrite Shoulder and/or Elbow by parameters
  if (parser.seenval('S')) pos.a = parser.value_float();
  if (parser.seenval('E')) pos.b = parser.value_float();

  if (cur_pos != pos) {
    if (_check_if_running()) return;

    // transform joint angles back to stepper positions
    x_scara_relative_to_delta(pos);
    forward_kinematics_SCARA(pos.a, pos.b);
    x_scara_delta_to_relative(pos);

    // update current position to cartesian position
    current_position.set(cartes.x, cartes.y);
    sync_plan_position();
  }

  report_current_position();
}

/**
 * M363: X-SCARA - reserved for future use
 */
#include "../../module/endstops.h"

void GcodeSuite::M363() {
  
  bool home_x = parser.seen("X");
  bool home_y = parser.seen("Y");
  if (!home_x && !home_y) return;

  int old_mode = x_scara_coordinates_mode;
  x_scara_change_coordinates_mode(X_SCARA_COORDINATES_LOCK_XY);
  
  endstops.enable();

  if (home_x) {
    homeaxis(X_AXIS);
  }

  if (home_y) {
    homeaxis(Y_AXIS);
  }

  x_scara_change_coordinates_mode(old_mode);
  endstops.not_homing();
}

/**
 * M364: X-SCARA Version - return current scara version
 */

void GcodeSuite::M364() {
  

  #if ENABLED(X_SCARA_DEBUG)
    if (parser.seenval('D')) {
      x_scara_debug = parser.value_bool();
    }
    SERIAL_ECHOPGM(X_SCARA_VERSION_STR);
    SERIAL_ECHOLNPAIR(" (Debug:", x_scara_debug, ")");
  #else
    SERIAL_ECHOLNPGM(X_SCARA_VERSION_STR);
  #endif

}

#endif // X_SCARA
