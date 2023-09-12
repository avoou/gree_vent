

import serial
import logging
import codecs


_LOGGER = logging.getLogger(__name__)


# write serial const
MAX_SEND        = 21


class FHBQDVentilation:
    def __init__(self, port, name):
        self.name = name
        self.port = port
        self.vent_mode = None
        self.bypass_mode = None
        self.fan_speed = None
        self.vent_power = 'off'


    def get_SRL(self):
        self.SRL = serial.Serial(
            port=self.port, 
            baudrate=9600, 
            timeout=0.5
            )


    def refresh_status(self):
        status = self.read_status()
        if status['power'] != 'undefined': self.vent_power = status['power']
        if status['mode'] != 'undefined': self.vent_mode = status['mode']
        if status['speed'] != 'undefined': self.fan_speed = status['speed']
        if status['bypass'] != 'undefined': self.bypass_mode = status['bypass']



    def read_serial(self, SRL, q):
        
        while True:
            data = SRL.read()
            if data == b'\x7e':
                data = data + SRL.read()       
                if data == b'\x7e\x7e':
                    if     q == 'hex':
                        data = data + SRL.read(15)
                        return data
                    else:
                        data = data + SRL.read(2) 
                        if     (q == 'revise' and data == b'\x7e\x7e\xc0\xff'):
                            data = data + SRL.read(13)
                            return data
                        if     (q == 'slave' and data == b'\x7e\x7e\x00\xa0'):
                            data = data + SRL.read(13)
                            return data
                        if     (q == 'master' and data == b'\x7e\x7e\xa0\x00'):
                            data = data + SRL.read(12)
                            return data

    # converting bytes on serial to dic
    def get_dic(self, data):
        dic = []
        for el in data:
            nel = hex(el)[2:4]
            nel = '0'+nel if len(nel) == 1 else nel
            dic.append(nel)
        return dic


    def HexToByte(self, hexStr):
        bytes_a = []
        for i in range(0, len(hexStr), 2):
            bytes_a.append(chr(int(hexStr[i:i+2], 16)))
        return ''.join( bytes_a )


    # getting checksum for packet hex 
    def get_checksum(self, packet):
        checksum = 0
        for el in packet:
            checksum ^= ord(el)
        checksum = str(list(hex(checksum))[2]) + str(list(hex(checksum))[3])
        return checksum



    # checking sended
    def checking_sended(self, SRL, send):

        check = self.get_dic(self.read_serial(SRL, 'revise'))
        del check[16]

        j = 4
        sum_check_byte = 0
        diff = []
        while j < 16:
            if check[j] == send[j]: 
                sum_check_byte += 1
            else: 
                diff.append(j)
            j += 1
        
        if sum_check_byte == 12: 
            ch_ret = 'OK'
        else: 
            ch_ret = 'ERROR'

        #if send[9] == check[9] and send[10] == check[10] and send[13] == check[13]:
            #ch_ret = 'OK'
        #else: 
            #ch_ret = 'ERROR'
        
        return ch_ret


    #reading current status for output
    def read_status(self):
        with serial.Serial(
            port=self.port, 
            baudrate=9600, 
            timeout=0.5
            ) as SRL:

            status = {
                'mode': 'undefined',
                'speed': 'undefined',
                'bypass': 'undefined',
                'power': 'undefined'
            }
            
            while True:
                rx = self.get_dic(self.read_serial(SRL, 'revise'))

                if (rx[9] == '0a' or rx[9] == '2a' or rx[9] == '4a'   or rx[9] == '07' or rx[9] == '27' or rx[9] == '47'):
                    status['power'] = 'off'
                    break
                else:
                    status['power'] = 'on'

                    if (rx[9] == '8a' or rx[9] == '87'): 
                        status['bypass'] = 'auto'
                    if (rx[9] == 'aa' or rx[9] == 'a7'): 
                        status['bypass'] = 'on'
                    if (rx[9] == 'ca' or rx[9] == 'c7'): 
                        status['bypass'] = 'off'

                    if (rx[13] == '00' or rx[13] == '20'):
                        if rx[10] == '0c': 
                            status['mode'] = 'normal'
                            status['speed'] = '1'
                        if rx[10] == '12': 
                            status['mode'] = 'normal'
                            status['speed'] = '2'
                        if rx[10] == '21': 
                            status['mode'] = 'normal'
                            status['speed'] = '3'
                        if rx[10] == '4a': 
                            status['mode'] = 'normal exhaust'
                            status['speed'] = '1'
                        if rx[10] == '51': 
                            status['mode'] = 'normal exhaust'
                            status['speed'] = '3'
                        if rx[10] == '94': 
                            status['mode'] = 'normal supply'
                            status['speed'] = '1'
                        if rx[10] == 'a2': 
                            status['mode'] = 'normal supply'
                            status['speed'] = '3'

                    if rx[13] == '10':
                        if rx[10] == '0c': 
                            status['mode'] = 'save'
                            status['speed'] = '1'
                        if rx[10] == '12': 
                            status['mode'] = 'save'
                            status['speed'] = '2'
                        if rx[10] == '21': 
                            status['mode'] = 'save'
                            status['speed'] = '3'
                        if rx[10] == '4a': 
                            status['mode'] = 'save exhaust'
                            status['speed'] = '1'
                        if rx[10] == '51': 
                            status['mode'] = 'save exhaust'
                            status['speed'] = '3'
                        if rx[10] == '94': 
                            status['mode'] = 'save supply'
                            status['speed'] = '1'
                        if rx[10] == 'a2': 
                            status['mode'] = 'save supply'
                            status['speed'] = '3'
                
                break

            return status


    #runing command
    def run_com(self, cm):
        with serial.Serial(
            port=self.port, 
            baudrate=9600, 
            timeout=0.5
            ) as SRL:

            while True:
                

                
                rx = self.get_dic(self.read_serial(SRL, 'revise'))
                rx[2] = '00'
                rx[3] = 'a0'

                if cm[0] == 'on':
                    if rx[9] == '0a': rx[9] = '8a'
                    if rx[9] == '2a': rx[9] = 'aa'
                    if rx[9] == '4a': rx[9] = 'ca'
                    if rx[9] == '07': rx[9] = '87'
                    if rx[9] == '27': rx[9] = 'a7'
                    if rx[9] == '47': rx[9] = 'c7'

                if cm[0] == 'off': 
                    if rx[9] == '8a': rx[9] = '0a'
                    if rx[9] == 'aa': rx[9] = '2a'
                    if rx[9] == 'ca': rx[9] = '4a'
                    if rx[9] == '87': rx[9] = '07'
                    if rx[9] == 'a7': rx[9] = '27'
                    if rx[9] == 'c7': rx[9] = '47'


                else:
                    if (cm[2] == 'auto' and rx[9] == '0a'): rx[9] = '8a'        #'bypass: auto; '
                    if (cm[2] == 'on' and rx[9] == '2a'):   rx[9] = 'aa'        #'bypass: on; '
                    if (cm[2] == 'off' and rx[9] == '4a'):  rx[9] = 'ca'        #'bypass: off; '
                    if (cm[2] == 'auto' and rx[9] == '07'): rx[9] = '87'        #'bypass: auto; '
                    if (cm[2] == 'on' and rx[9] == '27'):   rx[9] = 'a7'        #'bypass: on; '
                    if (cm[2] == 'off' and rx[9] == '47'):  rx[9] = 'c7'        #'bypass: off; '
                    if (cm[2] == 'auto'): rx[9] = '8a'
                    if (cm[2] == 'on'): rx[9] = 'aa'
                    if (cm[2] == 'off'): rx[9] = 'ca'
                    
                    if (cm[0] == 'normal' or cm[0] == 'normal exhaust' or cm[0] == 'normal supply'):
                        rx[13] = '20'
                        #rx[13] = '00'
                        if (cm[0] == 'normal' and cm[1] == '1'): rx[10] = '0c'         #'mode: normal; speed: 1; '
                        if (cm[0] == 'normal' and cm[1] == '2'): rx[10] = '12'         #'mode: normal; speed: 2; '
                        if (cm[0] == 'normal' and cm[1] == '3'): rx[10] = '21'         #'mode: normal; speed: 3; '
                        if (cm[0] == 'normal exhaust' and cm[1] == '1'): rx[10] = '4a'        #'mode: normal exhaust; speed: 1; '
                        if (cm[0] == 'normal exhaust' and cm[1] == '2'): rx[10] = '51'        #'mode: normal exhaust; speed: 2)); '
                        if (cm[0] == 'normal exhaust' and cm[1] == '3'): rx[10] = '51'        #'mode: normal exhaust; speed: 3; '
                        if (cm[0] == 'normal supply' and cm[1] == '1'): rx[10] = '94'        #'mode: normal supply; speed: 1; '
                        if (cm[0] == 'normal supply' and cm[1] == '2'): rx[10] = 'a2'        #'mode: normal supply; speed: 2)); '
                        if (cm[0] == 'normal supply' and cm[1] == '3'): rx[10] = 'a2'        #'mode: normal supply; speed: 3; '
                    if (cm[0] == 'save' or cm[0] == 'save exhaust' or cm[0] == 'save supply'):
                        rx[13] = '10'
                        if (cm[0] == 'save' and cm[1] == '1'): rx[10] = '0c'         #'mode: save; speed: 1; '
                        if (cm[0] == 'save' and cm[1] == '2'): rx[10] = '12'         #'mode: save; speed: 2; '
                        if (cm[0] == 'save' and cm[1] == '3'): rx[10] = '21'         #'mode: save; speed: 3; '
                        if (cm[0] == 'save exhaust' and cm[1] == '1'): rx[10] = '4a'        #'mode: save exhaust; speed: 1; '
                        if (cm[0] == 'save exhaust' and cm[1] == '2'): rx[10] = '51'        #'mode: save exhaust; speed: 2; '
                        if (cm[0] == 'save exhaust' and cm[1] == '3'): rx[10] = '51'        #'mode: save exhaust; speed: 3; '
                        if (cm[0] == 'save supply' and cm[1] == '1'): rx[10] = '94'        #'mode: save supply; speed: 1; '
                        if (cm[0] == 'save supply' and cm[1] == '2'): rx[10] = 'a2'        #'mode: save supply; speed: 2; '
                        if (cm[0] == 'save supply' and cm[1] == '3'): rx[10] = 'a2'        #'mode: save supply; speed: 3; '
                
                del rx[16]
                
                packet = self.HexToByte(''.join(rx))
                checksum = self.get_checksum(packet)
                
                com = ''.join(rx)+checksum
                
                answer = ''
                i = 1
                while answer != 'OK':
                    if i > MAX_SEND:
                        _LOGGER.warning("in switch.py runcom def, count sended: ", i) 
                        break

                    SRL.write(codecs.decode(com, 'hex_codec'))
                    answer = self.checking_sended(SRL, rx)
                    i += 1
                    
                break

            _LOGGER.warning("in switch.py runcom def, answer: ", answer)

            if answer != "OK": 
                return 'ERROR'
            
            if answer == "OK": 
                return 'OK'
