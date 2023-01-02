import time
import smbus
import math
from BMP388 import *
from LSM6DSL import *
from LIS3MDL import *

class Sensor(object):
    def __init__(self, address=None):
        self._address = address
        self._bus = smbus.SMBus(0x01)

    # These are used by all sensors. Note that the address values
    # are set when running __init__.
    def _read_byte(self, cmd):
        return self._bus.read_byte_data(self._address, cmd)

    def _read_s8(self, cmd):
        result = self._read_byte(cmd)
        if result > 128:
            result -= 256
        return result

    def _read_u16(self, cmd):
        LSB = self._bus.read_byte_data(self._address, cmd)
        MSB = self._bus.read_byte_data(self._address, cmd + 0x01)
        return (MSB << 0x08) + LSB

    def _read_s16(self, cmd):
        result = self._read_u16(cmd)
        if result > 32767:
            result -= 65536
        return result

    def _write_byte(self, cmd, val):
        self._bus.write_byte_data(self._address, cmd, val)

class SensorNotAvailableException(Exception):
    'Raised when sensor is not available'
    pass
    

class Pressure(Sensor):
    def __init__(self, address=BMP388_ADDRESS):
        super().__init__(address=address)

        if self.sensor_available() != 'BMP388':
            raise SensorNotAvailableException('Pressure sensor not available')

        self.sensor_reset()

    def sensor_reset(self):
        # Setup sensor
        u8RegData = self._read_byte(BMP388_REG_ADD_STATUS)
        if u8RegData & BMP388_REG_VAL_CMD_RDY:
            self._write_byte(BMP388_REG_ADD_CMD,
                             BMP388_REG_VAL_SOFT_RESET)
            time.sleep(0.01)

        self._write_byte(BMP388_REG_ADD_PWR_CTRL,
                         BMP388_REG_VAL_PRESS_EN
                         | BMP388_REG_VAL_TEMP_EN
                         | BMP388_REG_VAL_NORMAL_MODE)
        self._load_calibration()

    def sensor_available(self):
        if self._read_byte(BMP388_REG_ADD_WIA) == BMP388_REG_VAL_WIA:
            #print("Pressure sersor is BMP388!\r\n")
            return 'BMP388'
        else:
            #print ("Pressure sersor NULL!\r\n")
            return None
        

    def _load_calibration(self):
        self.T1 = self._read_u16(BMP388_REG_ADD_T1_LSB)
        self.T2 = self._read_u16(BMP388_REG_ADD_T2_LSB)
        self.T3 = self._read_s8(BMP388_REG_ADD_T3)
        self.P1 = self._read_s16(BMP388_REG_ADD_P1_LSB)
        self.P2 = self._read_s16(BMP388_REG_ADD_P2_LSB)
        self.P3 = self._read_s8(BMP388_REG_ADD_P3)
        self.P4 = self._read_s8(BMP388_REG_ADD_P4)
        self.P5 = self._read_u16(BMP388_REG_ADD_P5_LSB)
        self.P6 = self._read_u16(BMP388_REG_ADD_P6_LSB)
        self.P7 = self._read_s8(BMP388_REG_ADD_P7)
        self.P8 = self._read_s8(BMP388_REG_ADD_P8)
        self.P9 = self._read_s16(BMP388_REG_ADD_P9_LSB)
        self.P10 = self._read_s8(BMP388_REG_ADD_P10)
        self.P11 = self._read_s8(BMP388_REG_ADD_P11)

    def compensate_temperature(self, adc_T):
        partial_data1 = adc_T - 256 * self.T1
        partial_data2 = self.T2 * partial_data1
        partial_data3 = partial_data1 * partial_data1
        partial_data4 = partial_data3 * self.T3
        partial_data5 = partial_data2 * 262144 + partial_data4
        partial_data6 = partial_data5 / 4294967296
        self.T_fine = partial_data6
        comp_temp = partial_data6 * 25 / 16384
        return comp_temp

    def compensate_pressure(self, adc_P):
        partial_data1 = self.T_fine * self.T_fine
        partial_data2 = partial_data1 / 0x40
        partial_data3 = partial_data2 * self.T_fine / 256
        partial_data4 = self.P8 * partial_data3 / 0x20
        partial_data5 = self.P7 * partial_data1 * 0x10
        partial_data6 = self.P6 * self.T_fine * 4194304
        offset = self.P5 * 140737488355328 + partial_data4 \
            + partial_data5 + partial_data6

        partial_data2 = self.P4 * partial_data3 / 0x20
        partial_data4 = self.P3 * partial_data1 * 0x04
        partial_data5 = (self.P2 - 16384) * self.T_fine * 2097152
        sensitivity = (self.P1 - 16384) * 70368744177664 \
            + partial_data2 + partial_data4 + partial_data5

        partial_data1 = sensitivity / 16777216 * adc_P
        partial_data2 = self.P10 * self.T_fine
        partial_data3 = partial_data2 + 65536 * self.P9
        partial_data4 = partial_data3 * adc_P / 8192
        partial_data5 = partial_data4 * adc_P / 512
        partial_data6 = adc_P * adc_P
        partial_data2 = self.P11 * partial_data6 / 65536
        partial_data3 = partial_data2 * adc_P / 128
        partial_data4 = offset / 0x04 + partial_data1 + partial_data5 \
            + partial_data3
        comp_press = partial_data4 * 25 / 1099511627776
        return comp_press

    def get_data(self):
        xlsb = self._read_byte(BMP388_REG_ADD_TEMP_XLSB)
        lsb = self._read_byte(BMP388_REG_ADD_TEMP_LSB)
        msb = self._read_byte(BMP388_REG_ADD_TEMP_MSB)
        adc_T = (msb << 0x10) + (lsb << 0x08) + xlsb
        temperature = self.compensate_temperature(adc_T)
        
        xlsb = self._read_byte(BMP388_REG_ADD_PRESS_XLSB)
        lsb = self._read_byte(BMP388_REG_ADD_PRESS_LSB)
        msb = self._read_byte(BMP388_REG_ADD_PRESS_MSB)
        adc_P = (msb << 0x10) + (lsb << 0x08) + xlsb
        pressure = self.compensate_pressure(adc_P)
    
        return {'temp_K':temperature/100,
                'press_hPa':pressure/100/100}

class AccelGyro(Sensor):
    def __init__(self, address=LSM6DSL_ADDRESS):
        super().__init__(address=address)

        if self.sensor_available() != 'LSM6DSL':
            raise SensorNotAvailableException('Accelerometer not available')

        self.sensor_reset()

    def sensor_reset(self):
        # Setup sensor
        #initialise the accelerometer
        self._write_byte(LSM6DSL_CTRL1_XL,0b10011111)           #ODR 3.33 kHz, +/- 8g , BW = 400hz
        self._write_byte(LSM6DSL_CTRL8_XL,0b11001000)           #Low pass filter enabled, BW9, composite filter
        self._write_byte(LSM6DSL_CTRL3_C,0b01000100)            #Enable Block Data update, increment during multi byte read
        self.A_SCALE = 0.244
        
        #initialise the gyroscope
        self._write_byte(LSM6DSL_CTRL2_G,0b10011100)            #ODR 3.3 kHz, 2000 dps
        self.G_GAIN = 0.070          # [deg/s/LSB]  If you change the dps for gyro, you need to update this value accordingly

        
    def sensor_available(self):
        LSM6DSL_WHO_AM_I_response = (self._read_byte(LSM6DSL_WHO_AM_I))
        if LSM6DSL_WHO_AM_I_response == 0x6A:
            return 'LSM6DSL'
        else:
            return None

    def get_data(self):
        return {'acc_x_mg': self._read_s16(LSM6DSL_OUTX_L_XL)*self.A_SCALE,
                'acc_y_mg': self._read_s16(LSM6DSL_OUTY_L_XL)*self.A_SCALE,
                'acc_z_mg': self._read_s16(LSM6DSL_OUTZ_L_XL)*self.A_SCALE,
                'gyr_x_dps': self._read_s16(LSM6DSL_OUTX_L_G)*self.G_GAIN,
                'gyr_y_dps': self._read_s16(LSM6DSL_OUTY_L_G)*self.G_GAIN,
                'gyr_z_dps': self._read_s16(LSM6DSL_OUTZ_L_G)*self.G_GAIN}

class Mag(Sensor):
    def __init__(self, address=LIS3MDL_ADDRESS):
        super().__init__(address=address)

        if self.sensor_available() != 'LIS3MDL':
            raise SensorNotAvailableException('Magnetometer not available')

        self.sensor_reset()

    def sensor_reset(self):
        # Setup sensor
        #initialise the magnetometer
        self._write_byte(LIS3MDL_CTRL_REG1, 0b11011100)         # Temp sensor enabled, High performance, ODR 80 Hz, FAST ODR disabled and self test disabled.
        self._write_byte(LIS3MDL_CTRL_REG2, 0b00100000)         # +/- 8 gauss
        self._write_byte(LIS3MDL_CTRL_REG3, 0b00000000)         # Continuous-conversion mode
        
    def sensor_available(self):
        LIS3MDL_WHO_AM_I_response = (self._read_byte(LIS3MDL_WHO_AM_I))
        if LIS3MDL_WHO_AM_I_response == 0x3D:
            return 'LIS3MDL'
        else:
            return None

    def get_data(self):
        return {'mag_x': self._read_s16(LIS3MDL_OUT_X_L),
                'mag_y': self._read_s16(LIS3MDL_OUT_Y_L),
                'mag_z': self._read_s16(LIS3MDL_OUT_Z_L)}


RAD_TO_DEG = 57.29578
M_PI = 3.14159265358979323846

def get_rotation_angles(acd):
    # Rotation_angles
    accXangle =  (math.atan2(acd['acc_y_mg'],acd['acc_z_mg'])*RAD_TO_DEG)
    accYangle =  (math.atan2(acd['acc_z_mg'],acd['acc_x_mg'])+M_PI)*RAD_TO_DEG
    if accYangle > 90:
        accYangle -= 270.0
    else:
        accYangle += 90.0
    return accXangle, accYangle

def get_heading(md):
    #Calculate heading
    heading = 180 * math.atan2(md['mag_y'],md['mag_x'])/M_PI

    #Only have our heading between 0 and 360
    if heading < 0:
        heading += 360
    return heading

def tilt_compensated_heading(acd, md):
    # Tilt compensation
    accTotal = math.sqrt(acd['acc_x_mg']**2 +
                         acd['acc_y_mg']**2 +
                         acd['acc_z_mg']**2)
    accXnorm = acd['acc_x_mg']/accTotal
    accYnorm = acd['acc_y_mg']/accTotal

    #Calculate pitch and roll
    pitch = math.asin(accXnorm)
    roll = -math.asin(accYnorm/math.cos(pitch))

    magXcomp = md['mag_x']*math.cos(pitch)+md['mag_z']*math.sin(pitch)
    magYcomp = md['mag_x']*math.sin(roll)*math.sin(pitch)+md['mag_y']*math.cos(roll)-md['mag_z']*math.sin(roll)*math.cos(pitch)
    tiltCompensatedHeading = 180 * math.atan2(magYcomp,magXcomp)/M_PI
    if tiltCompensatedHeading < 0:
        tiltCompensatedHeading += 360

    return tiltCompensatedHeading, pitch*RAD_TO_DEG, roll*RAD_TO_DEG
