"""
Decision-making logic.
"""

import math

from pymavlink import mavutil

from ..common.modules.logger import logger
from ..telemetry import telemetry


class Position:
    """
    3D vector struct.
    """

    def __init__(self, x: float, y: float, z: float) -> None:
        self.x = x
        self.y = y
        self.z = z


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
HEIGHT_TOLERANCE = 0.5
ANGLE_TOLERANCE = 5
Z_SPEED = 1
TURNING_SPEED = 5
RELATIVE = 1


class Command:  # pylint: disable=too-many-instance-attributes
    """
    Command class to make a decision based on recieved telemetry,
    and send out commands based upon the data.
    """

    __private_key = object()

    @classmethod
    def create(
        cls,
        connection: mavutil.mavfile,
        target: Position,
        local_logger: logger.Logger,
    ) -> "tuple[bool, Command | None]":
        """
        Falliable create (instantiation) method to create a Command object.
        """
        if connection is None:
            local_logger.error("Failed to create Command. No connection provided.", True)
            return False, None

        if target is None:
            local_logger.error("Failed to create Command. No target provided.", True)
            return False, None

        return True, cls(cls.__private_key, connection, target, local_logger)

    def __init__(
        self,
        key: object,
        connection: mavutil.mavfile,
        target: Position,
        local_logger: logger.Logger,
    ) -> None:
        assert key is Command.__private_key, "Use create() method"

        self.__connection = connection
        self.__target = target
        self.__logger = local_logger

        self.__velocity_count = 0
        self.__x_velocity_sum = 0.0
        self.__y_velocity_sum = 0.0
        self.__z_velocity_sum = 0.0

    def __normalize_angle_degrees(self, angle: float) -> float:
        """
        Normalize angle to [-180, 180].
        """
        return (angle + 180) % 360 - 180

    def run(self, telemetry_data: telemetry.TelemetryData) -> "tuple[bool, str | None]":
        """
        Make a decision based on received telemetry data.
        """

        if telemetry_data is None:
            self.__logger.warning("No telemetry data received", True)
            return False, None

        # Log average velocity for this trip so far

        self.__velocity_count += 1
        self.__x_velocity_sum += telemetry_data.x_velocity or 0.0
        self.__y_velocity_sum += telemetry_data.y_velocity or 0.0
        self.__z_velocity_sum += telemetry_data.z_velocity or 0.0

        avg_x = self.__x_velocity_sum / self.__velocity_count
        avg_y = self.__y_velocity_sum / self.__velocity_count
        avg_z = self.__z_velocity_sum / self.__velocity_count

        self.__logger.info(f"Average velocity: ({avg_x}, {avg_y}, {avg_z})", True)

        # Use COMMAND_LONG (76) message, assume the target_system=1 and target_componenet=0
        # The appropriate commands to use are instructed below

        # Adjust height using the comand MAV_CMD_CONDITION_CHANGE_ALT (113)
        # String to return to main: "CHANGE_ALTITUDE: {amount you changed it by, delta height in meters}"

        # Adjust direction (yaw) using MAV_CMD_CONDITION_YAW (115). Must use relative angle to current state
        # String to return to main: "CHANGING_YAW: {degree you changed it by in range [-180, 180]}"
        # Positive angle is counter-clockwise as in a right handed system

        # altitude correction
        delta_z = self.__target.z - telemetry_data.z

        if abs(delta_z) > HEIGHT_TOLERANCE:
            self.__connection.mav.command_long_send(
                1,
                0,
                mavutil.mavlink.MAV_CMD_CONDITION_CHANGE_ALT,
                0,
                Z_SPEED,
                0,
                0,
                0,
                0,
                0,
                self.__target.z,
            )

            output = f"CHANGE_ALTITUDE: {delta_z}"
            return True, output

        # yaw correction
        target_angle = math.atan2(
            self.__target.y - telemetry_data.y,
            self.__target.x - telemetry_data.x,
        )
        target_angle_degrees = math.degrees(target_angle)
        current_yaw_degrees = math.degrees(telemetry_data.yaw)

        delta_yaw = self.__normalize_angle_degrees(target_angle_degrees - current_yaw_degrees)

        if abs(delta_yaw) > ANGLE_TOLERANCE:
            self.__connection.mav.command_long_send(
                1,
                0,
                mavutil.mavlink.MAV_CMD_CONDITION_YAW,
                0,
                delta_yaw,
                TURNING_SPEED,
                0,
                RELATIVE,
                0,
                0,
                0,
            )

            output = f"CHANGE_YAW: {delta_yaw}"
            return True, output

        return True, None


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
