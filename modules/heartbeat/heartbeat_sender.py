"""
Heartbeat sending logic.
"""

from pymavlink import mavutil
from modules.common.modules.logger import logger

# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
class HeartbeatSender:
    """
    HeartbeatSender class to send a heartbeat
    """

    __private_key = object()

    @classmethod
    def create(
        cls,
        connection: mavutil.mavfile,
        heartbeat_sender_logger: logger.Logger 
    ) -> "tuple[True, HeartbeatSender] | tuple[False, None]":
        """
        Falliable create (instantiation) method to create a HeartbeatSender object.
        """
        
        if connection is None:
            heartbeat_sender_logger.error("HeartbeatSender creation failed. No connection provided (Connection is None).", True)
            return False, None

        return True, cls(cls.__private_key, connection, heartbeat_sender_logger)

    def __init__(
        self,
        key: object,
        connection: mavutil.mavfile,
        heartbeat_sender_logger: logger.Logger
    ):
        assert key is HeartbeatSender.__private_key, "Use create() method"

        # Do any intializiation here
        self.__connection = connection
        self.__heartbeat_sender_logger = heartbeat_sender_logger
        

    def run(self):
        """
        Attempt to send a heartbeat message.
        """
        try:
            self.__connection.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_GCS,
                                                 mavutil.mavlink.MAV_AUTOPILOT_INVALID,
                                                 0,
                                                 0,
                                                 mavutil.mavlink.MAV_STATE_ACTIVE)
        
        except Exception as e:
            self.__heartbeat_sender_logger.error(f"Failed to send heartbeat message: {e}", True)
            return False

        self.__heartbeat_sender_logger.info("Heartbeat sent", True)
        return True
        


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
