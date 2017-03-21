# -*- coding: utf-8 -*-
import os
import time
import binascii
import unittest

import smspdu

class SMS_PDU_Test(unittest.TestCase):

    def test_encoding_7_bit(self):
        from smspdu.pdu import pack7bit
        input = 'hellohello'
        # h = 0b1101000
        # e = 0b1100101
        # l = 0b1101100
        # o = 0b1101111
        # packed is    11101000 00110010 10011011 1111101 110

        # packed is    11101000 00110010 10011011 11111101 01000110 
        output_bytes =[0xE8,    0x32,    0x9B,    0xFD,    0x46,    0x97, 0xD9, 0xEC, 0x37]
        output = ''.join(chr(x) for x in output_bytes)
        self.assertEquals(pack7bit(input)[1], output)

    def test_encoding_7_bit_header(self):
        from smspdu.pdu import pack7bit
        input = 'abcd'
        # a = 0b1100001
        # b = 0b1100010
        # c = 0b1100011
        # d = 0b1100100
        # packed is     01100001 11110001 10011000 00001100
        output_bytes = [0x61,    0xf1,    0x98,    0x0c]
        output = ''.join(chr(x) for x in output_bytes)
        self.assertEquals(pack7bit(input)[1], output)

        # packed is     01000000 01011000 00111100 00100110 00000011

        output_bytes = [0x40,    0x58,    0x3c,    0x26,    0x03]
        output = ''.join(chr(x) for x in output_bytes)
        self.assertEquals(pack7bit(input, 1)[1], output)

    def test_decoding_7_bit(self):
        from smspdu.pdu import unpack7bit
        input_bytes = [0xE8, 0x32, 0x9B, 0xFD, 0x46, 0x97, 0xD9, 0xEC, 0x37]
        input = ''.join(chr(x) for x in input_bytes)
        output = 'hellohello'
        self.assertEquals(unpack7bit(input), output)

    def test_nibbleswap(self):
        from smspdu.pdu import nibbleswap
        input_bytes =[0xE8, 0x32, 0x9B, 0xFD, 0x46, 0x97, 0xD9, 0xEC, 0x37]
        input = ''.join(chr(x) for x in input_bytes)
        output_bytes =[0x8E, 0x23, 0xB9, 0xDF, 0x64, 0x79, 0x9D, 0xCE, 0x73]
        output = ''.join(chr(x) for x in output_bytes)
        self.assertEquals(nibbleswap(input), output)

    def test_phoneNumberPacking(self):
        from smspdu.pdu import unpackPhoneNumber, packPhoneNumber
        ae = self.assertEquals
        input = ''.join([chr(x) for x in
                                (0x72, 0x38, 0x88, 0x09, 0x00, 0xF1)])
        output = '27838890001'
        ae(unpackPhoneNumber(input), output)
        ae(packPhoneNumber(output), input)

    def test_tpdu_encode(self):
        p = smspdu.SMS_DELIVER.create('+46708251358', 'test', u'hellohello',
            datestamp=time.mktime((2009, 8, 7, 6, 5, 4, 0, 0, -1)),
            tp_sri=1, tp_mms=0)
        self.assertEquals(p.toPDU(),
                '200B916407281553F80000908070605040000AE8329BFD4697D9EC37')
        # sanity - check decode matches input
        s = smspdu.SMS_DELIVER.fromPDU(p.toPDU(), '46708251358')
        self.assertEquals(s.tp_address, u'+46708251358')
        self.assertEquals(s.tp_scts, u'09080706050400')
        self.assertEquals(s.user_data, u'hellohello')

    def test_tpdu_encode_alpha_sender(self):
        p = smspdu.SMS_DELIVER.create('eKit', 'test', u'hellohello',
            datestamp=time.mktime((2009, 8, 7, 6, 5, 4, 3, 0, -1)),
            tp_sri=1, tp_mms=0)
        self.assertEquals(p.toPDU(),
            '2008D0E5659A0E0000908070605040000AE8329BFD4697D9EC37')
        s = smspdu.SMS_DELIVER.fromPDU(p.toPDU(), '46708251358')
        self.assertEquals(s.tp_address, u'eKit')
        self.assertEquals(s.tp_scts, u'09080706050400')
        self.assertEquals(s.user_data, u'hellohello')

    def test_tpdu_encode_gsm(self):
        p = smspdu.SMS_DELIVER.create('46708251358', 'test', u'h\u20ACllohello',
            datestamp=time.mktime((2009, 8, 7, 6, 5, 4, 3, 0, 0)))
        s = smspdu.SMS_DELIVER.fromPDU(p.toPDU(), '46708251358', 'test')
        self.assertEquals(s.tp_oa, '46708251358')
        self.assertEquals(s.user_data, u'h\u20ACllohello')

    def test_tpdu_encode_ucs2(self):
        p = smspdu.SMS_DELIVER.create('46708251358', 'test', u'h\u20ADllohello',
            datestamp=time.mktime((2009, 8, 7, 6, 5, 4, 3, 0, 0)))
        s = smspdu.SMS_DELIVER.fromPDU(p.toPDU(), '46708251358', 'test')
        self.assertEquals(s.tp_oa, '46708251358')
        self.assertEquals(s.user_data, u'h\u20ADllohello')

    def test_gsm_encode(self):
        c = smspdu.gsm0338()
        self.assertEquals(c.encode('hello'), 'hello')
        self.assertEquals(c.encode(u'\u20AC'), '\x1b\x65')
        self.assertRaises(UnicodeError, c.encode, u'\u20AD')

    def test_tpdu_decode(self):
        s = smspdu.SMS_SUBMIT.fromPDU(
            '11010b911614261771f000000b0ae8329bfd4697d9ec37',
            '447924449999', 'test')
        self.assertEquals(s.tp_address, '+61416271170')
        self.assertEquals(s.user_data, 'hellohello')

    def test_tpdu_decode_sample_deliver(self):
        s = smspdu.SMS_DELIVER.fromPDU(
            '040BC87238880900F10000993092516195800AE8329BFD4697D9EC37',
            'dummy', 'test')
        self.assertEquals(s.tp_address, '27838890001')
        self.assertEquals(s.user_data, 'hellohello')

    def test_tpdu_decode_utf16(self):
        s = smspdu.SMS_SUBMIT.fromPDU(
            '11040b911614123234f10008ff2a00480065006c006c006f00200070006f006f007000790068006500610064002000a9002000ae002000a1',
            '447924421430', 'test')
        self.assertEquals(s.user_data, u'Hello poopyhead \xa9 \xae \xa1')

    def test_tpdu_decode_udhi(self):
        smspdu.SMS_SUBMIT.fromPDU(
            '51210a8140111586850000ffa00500030203018eea73fbdc3eb7cfed73fbdc3eb7cfed73fbdc3eb7cfed73fbdc3eb7cfed73fbdc3eb7cfed73fbdc3eb7cfed73fbdc3eb7cfed73fbdc3eb7cfed73db4576915d6417d94576915d6417d94586b7e16d781bde86b7e16d781bde86b7e16d781bde86b7e16d781bde86b7e16d781bde86b7e16d781bde86b7e16d781bde86b7e16d781bde86b7e1',
            '447924449999', 'test')

    def test_sms_decode_8bit(self):
        # this is busted.
        # 2007-05-08 17:07:12,239 mvnoweb.controllers DEBUG got MO SMS
        # '`?'('5108038154f30004ff0906050415cc000060d8') for 447924400659
        # GSM 03.38:
        # 6.2.2           8 bit data
        # 8 bit data is user defined
        # SMS User Data Length meaning: Number of octets
        # Padding:        CR in the case of an 8 bit character set
        #                 Otherwise - user defined
        # Character table:              User Specific
        smspdu.SMS_SUBMIT.fromPDU('5107038154f30004ff0906050415cc000060d8',
            '447924449999')

    def test_sms_decode_wackychars(self):
        # wacky characters with eyeballs (ok, umlauts) and shit
        ae = self.assertEquals
        s = smspdu.SMS_SUBMIT.fromPDU(
            '110a0b911614261771f00000ff18c8342800da944103d05701da17d2fdf7a3e3cf7b12',
            '447924449999')
        ae(s.user_data, u'Hi £ € ¥ §\n äéiñoåæüyßÇ')


    def test_sms_decode_businesscard(self):
        # a nokia business card. kill me now.
        ae = self.assertEquals
        s = smspdu.SMS_SUBMIT.fromPDU(
            '550d0b911614261771f000f5a78c0b050423f423f40003010201424547494e3a56434152440d0a56455253494f4e3a322e310d0a4e3a4d650d0a54454c3b505245463b43454c4c3b564f4943453a2b36313431363237313137300d0a54454c3b484f4d453b564f4943453a2b36313339353337303437310d0a54454c3b574f524b3b564f4943453a2b36313339363734373031350d0a454e443a',
            '447924449999')
        ae(s.user_data, u'BEGIN:VCARD\r\nVERSION:2.1\r\nN:Me\r\nTEL;PREF;CELL;VOICE:+61416271170\r\nTEL;HOME;VOICE:+61395370471\r\nTEL;WORK;VOICE:+61396747015\r\nEND:')

    def test_sms_decode_wackychars2(self):
        # more wacky characters
        ae = self.assertEquals
        s = smspdu.SMS_SUBMIT.fromPDU(
            '150f0b911614261771f00008ff3e0054006800690073002000690073002000460055004e0020002d00280029005f003c003e005b005d007b007d0060002700a100bf0023007c003a002f003b',
            '447924449999', 'test')
        ae(s.user_data, u"This is FUN -()_<>[]{}`'\xa1\xbf#|:/;")


    def test_sms_decode_longmsg(self):
        ae = self.assertEquals
        s = smspdu.SMS_SUBMIT.fromPDU(
            '51000a8140713299430000ffa005000386020194f5391dc40ebbc9653228ed0631df6ef2db1d0205efe1343ded3e83d0e5301d2d7fdf41e3fa9cfe6ecf5d2e17e89a66b341e6b49b0c0acee96f39c89a1e83e8e8b21bf4369b41e6b71c1406ddc3ec75ab8c87b3dff232083546d7e5637479bee99ddff6131d740fb3d72077392c07d1d1e176799e0235d367341d747e83e86f10354c2fbb40',
            '447924449999', 'test')
        ae(s.user_data, u"Just landed in London! Awaiting heathrow customs... Will find Astor Vic then off for a walk-explore (churches~gov't walk near thames) Might go to Tate. ")

    def test_sms_decode_whoknows(self):
        smspdu.SMS_SUBMIT.fromPDU(
            '5100038154f300040b1806050415ccc00160d99b56ac1ab460c583170d59346a0000',
            '44332211', 'test')

    def test_sms_decode_siemensbrackets(self):
        # 7 bit GSM 0338 with extension table, yay
        ae = self.assertEquals
        s = smspdu.SMS_SUBMIT.fromPDU(
            '11140b911614261771f000000b0d41f9190ddaf036a84d6ae303',
            '44332211', 'test')
        ae(s.user_data, u"Argh [{}]")

    def test_sms_decode_pid32(self):
        # 7 bit GSM 0338 with extension table, yay
        ae = self.assertEquals
        s = smspdu.SMS_SUBMIT.fromPDU('11180a81004336384432000b00', '44332211', 'test')

    def test_sms_multipart_16(self):
        ae = self.assertEquals
        part1 = '51050b911614123234f10000ffa00608040005030154741914afa7c76b9058febebb41e6371ea4aeb7e16532e86d2fcb41747419a40eebf520f2fbec0251d16550bc9e1eaf4162f9fbee0699df7890bade8697c9a0b7bd2c07d1d165903aacd783c8efb30b44459741f17a7abc0689e5efbb1b647ee341ea7a1b5e2683def6b21c44479741eab05e0f22bfcf2e10155d06c5ebe9f11a2496bfef'.upper()
        s1 = smspdu.SMS_SUBMIT.fromPDU(part1, '447924449999')
        ae(s1.concatInfo(), dict(size=16, ref=5, count=3, seq=1))
        ae(s1.user_data, 'The quick brown fox jumped over the jazz dog. The quick brown fox jumped over the jazz dog. The quick brown fox jumped over the jazz dog. The quick brow')
        ae(s1.user_data_headers, [(8, [0, 5, 3, 1])])
        part2 = '51060b911614123234f10000ffa0060804000503026e90f98d07a9eb6d78990c7adbcb72101d5d06a9c37a3d88fc3ebb4054741914afa7c76b9058febebb41e6371ea4aeb7e16532e86d2fcb41747419a40eebf520f2fbec0251d165903aacd783c4f2f7dd0d22bfcf2075bd0d2f93416f7b590ea2a3cba0783d3d5e83cc6fbc0b14140e8945e31199542e994de7131a954aa7d4aaf58acd6a5d'.upper()
        s2 = smspdu.SMS_SUBMIT.fromPDU(part2, '447924449999')
        ae(s2.user_data_headers, [(8, [0, 5, 3, 2])])
        ae(s2.user_data, 'n fox jumped over the jazz dog. The quick brown fox jumped over the jazz dog. The jazz brown dog jumped over the quick fox. ABCDEFGHIJKLMNOPQRRSTUVWXYZ.')
        part3 = '51070b911614123234f10000ff3706080400050303202aba0c8ad7d3e335482c7fdfdd20f31b0f52d7dbf03219f4b697e5203aba0c6287f57910f97d768100'.upper()
        s3 = smspdu.SMS_SUBMIT.fromPDU(part3, '447924449999')
        ae(s3.user_data_headers, [(8, [0, 5, 3, 3])])
        ae(s3.user_data, ' The quick brown fox jumped over the lazy dog. ')

        # check re-encoding

        # check re-encode
        p1 = smspdu.SMS_SUBMIT.create(s1.sender, s1.recipient,
            s1.user_data, s1.datestamp, tp_vpf=s1.tp_vpf,
            tp_vp=s1.tp_vp, tp_mr=s1.tp_mr,
            user_data_headers=s1.user_data_headers)
        ae(part1, p1.toPDU())
        p2 = smspdu.SMS_SUBMIT.create(s2.sender, s2.recipient,
            s2.user_data, s2.datestamp, tp_vpf=s2.tp_vpf,
            tp_vp=s2.tp_vp, tp_mr=s2.tp_mr,
            user_data_headers=s2.user_data_headers)
        ae(part2, p2.toPDU())
        p3 = smspdu.SMS_SUBMIT.create(s3.sender, s3.recipient,
            s3.user_data, s3.datestamp, tp_vpf=s3.tp_vpf,
            tp_vp=s3.tp_vp, tp_mr=s3.tp_mr,
            user_data_headers=s3.user_data_headers)
        ae(part3, p3.toPDU())


    def test_sms_multipart_8(self):
        ae = self.assertEquals
        part1 = '51670b911604578652f90000a7a0050003e002019a6fb91b342fe3f3e27a9b0542bfef2039a8fe0325e7a0fb5bbe0689ebf3fc0f742d83ece9799a0ea2a3cba0793bcc6697e774d0f85d77d3e579d03d6d06d1d16590387d2ecfe9a031ba2e1fa3413272380f42a1dfed32e86d06d1d16510fc0d2fa74026101d5d068ddf6cf67b3e2fd7db2014390c3287dbeffa1cd40ee341e976780e3ab3c3'.upper()
        s1 = smspdu.SMS_SUBMIT.fromPDU(part1, '447924449999')
        ae(s1.user_data_headers, [(0, [224, 2, 1])])
        ae(s1.user_data, 'Morn sexybum, how r u? Is work busy? We visit the smallest country wif the bigest church 2day (home of the pope) & the collosseum (da famous max imas gla')
        part2 = '51680b911604578652f90000a73b050003e00202c8e930fd2d778184f5349b9c769fe7203a3a4c07c94132180c9697cf416f36390462d6eda03a88fda6cf41d82708'.upper()
        s2 = smspdu.SMS_SUBMIT.fromPDU(part2, '447924449999')
        ae(s2.user_data_headers, [(0, [224, 2, 2])])
        ae(s2.user_data, 'diator. Buildings that r 2000yrs old! Luv u lots XO ')

        # check re-encode
        p1 = smspdu.SMS_SUBMIT.create(s1.sender, s1.recipient,
            s1.user_data, s1.datestamp, tp_vpf=s1.tp_vpf,
            tp_vp=s1.tp_vp, tp_mr=s1.tp_mr,
            user_data_headers=s1.user_data_headers)
        ae(part1, p1.toPDU())
        p2 = smspdu.SMS_SUBMIT.create(s2.sender, s2.recipient,
            s2.user_data, s2.datestamp, tp_vpf=s2.tp_vpf,
            tp_vp=s2.tp_vp, tp_mr=s2.tp_mr,
            user_data_headers=s2.user_data_headers)
        ae(part2, p2.toPDU())


    def test_pduspy(self):
        ae = self.assertEquals
        s = smspdu.SMS_SUBMIT.fromPDU(
            '6100008100002203060141A2A2D373507A0E0A83E6E9369C5D06D1CB733AA85D9ECFC3E732',
            '44321234', 'test')
        ae(u'This is a simple test message', s.user_data)
        s = smspdu.SMS_SUBMIT.fromPDU(
            '61000081000023042202008151D1E939283D078541F3741BCE2E83E8E5391DD42ECFE7E17319',
            '44321234', 'test')
        ae(u'This is a simple test message', s.user_data)
        s = smspdu.SMS_SUBMIT.fromPDU(
            '11130c914497424400600008ff080060006800690027',
            '44321234', 'test')
        ae(u"`hi'", s.user_data)

    def test_sms_nonnumeric_address(self):
        ae = self.assertEquals
        s = smspdu.SMS_SUBMIT.fromPDU(
            '110407d1e5659a0e0000ff33a8f2324d4f819ce53bc8fe4e8fcbed709aed021975a030c8fd76b7dae5b6b82c5704ddf37b590e4acf41d9e214',
            '44321234', 'test')
        ae(s.tp_address, 'eKit')

    def test_sms_corrupt_xml(self):
        smspdu.SMS_SUBMIT.fromPDU(
            '11110c9193337546419900f5ff8c2f2f53454f016b00285c7e80010001004e00000003766366084a6573732e766366424547494e3a56434152440d0a56455253494f4e3a322e310d0a464e3a4a6573730d0a4e3a4a6573730d0a54454c3b484f4d453a2b3339333335373634313439390d0a454e443a56434152440d0a0000000000000000000000000000000000000000000000000000000000',
            '44321234', 'test')

    def test_sim_download(self):
        t = '0408D0E5759A0E7FF6907090307513000824010101BB400101'
        tp = smspdu.SMS_DELIVER.fromPDU(t, 'test')
        message = '\x24\x01\x01\x01\xBB\x40\x01\x01'
        p = smspdu.SMS_DELIVER.create('ekit', 'test', message, tp_pid=0x7F,
            tp_dcs=0xF6, datestamp=tp.datestamp)
        self.assertEquals(p.toPDU(),
            '0008D0E5759A0E7FF6907090307513000824010101BB400101')

    def test_mwi(self):
        p = smspdu.SMS_DELIVER.create('eKit', 'test', u'hellohello',
            datestamp=time.mktime((2009, 8, 7, 6, 5, 4, 3, 0, -1)),
            tp_sri=1, tp_mms=0, tp_dcs=0xD8)
        # this hasn't actually been verified as correct
        self.assertEquals(p.toPDU(),
            '2008D0E5659A0E00D8908070605040000AE8329BFD4697D9EC37')

    def test_dcs0x01encoding(self):
        inpdu = '040C9144970393235500019090710275840006C6BADB9D0F01'
        tp = smspdu.SMS_DELIVER.fromPDU(inpdu, 'test')

        p = smspdu.SMS_DELIVER.create(tp.sender, 'test', tp.user_data,
            tp_pid=tp.tp_pid, tp_dcs=tp.tp_dcs, tp_mms=tp.tp_mms,
            datestamp=tp.datestamp)

        self.assertEquals(tp.tp_dcs, p.tp_dcs)
        self.assertEquals(tp.tp_ud, p.tp_ud)
        self.assertEquals(p.toPDU(), inpdu)

    def test_numericAddress(self):
        self.assertEquals(smspdu.SMS_SUBMIT.determineAddress('123'),
            (3, 0x81, '!\xf3'))

    def test_textAddress(self):
        from smspdu.pdu import pack7bit
        self.assertEquals(smspdu.SMS_SUBMIT.determineAddress('1test'),
            (10, 0xd0, pack7bit('1test')[1]))

    def test_dcs0xd1encoding(self):
        inpdu = '040AD1404141414100009011711262200001D7'
        tp = smspdu.SMS_DELIVER.fromPDU(inpdu, 'test')
        self.assertEquals(tp.tp_toa, 0xd0)
        self.assertEquals(tp.tp_oa, '$')

    def test_vpf_relative(self):
        # construct PDU
        p = smspdu.SMS_SUBMIT.create('eKit', 'test', u'hellohello',
            tp_vpf=2, tp_vp=143)
        self.assertEquals(p.tp_vpf, 2)
        self.assertEquals(p.tp_vp, 143)
        sp = p.toPDU()

        # back from PDU
        p2 = smspdu.SMS_SUBMIT.fromPDU(sp, 'test')
        self.assertEquals(p2.tp_vpf, 2)
        self.assertEquals(p2.tp_vp, 143)
        self.assertEquals(p2.toPDU(), sp)

    def test_vpf_absolute(self):
        # construct PDU
        p = smspdu.SMS_SUBMIT.create('eKit', 'test', u'hellohello',
            tp_vpf=3, tp_vp='10010112000000')
        self.assertEquals(p.tp_vpf, 3)
        self.assertEquals(p.tp_vp, '10010112000000')
        sp = p.toPDU()

        # back from PDU
        p2 = smspdu.SMS_SUBMIT.fromPDU(sp, 'test')
        self.assertEquals(p2.tp_vpf, 3)
        self.assertEquals(p2.tp_vp, '10010112000000')
        self.assertEquals(p2.toPDU(), sp)

    def test_vpf_extended(self):
        # not even going to try to construct a real extended VP - any old 7
        # octets will do
        vp = map(ord, 'ABCDEFG')
        hvp = binascii.hexlify(''.join(chr(i) for i in vp))

        # construct PDU
        p = smspdu.SMS_SUBMIT.create('eKit', 'test', u'hellohello',
            tp_vpf=1, tp_vp=vp)
        self.assertEquals(p.tp_vpf, 1)
        self.assertEquals(p.tp_vp, vp)
        sp = p.toPDU()

        # back from PDU
        p2 = smspdu.SMS_SUBMIT.fromPDU(sp, 'test')
        self.assertEquals(p2.tp_vpf, 1)
        self.assertEquals(p2.tp_vp, vp)
        self.assertEquals(p2.toPDU(), sp)

    def test_vpf_none(self):
        # construct PDU
        p = smspdu.SMS_SUBMIT.create('eKit', 'test', u'hellohello', tp_vpf=0)
        self.assertEquals(p.tp_vpf, 0)
        self.assertEquals(p.tp_vp, None)
        sp = p.toPDU()

        # back from PDU
        p2 = smspdu.SMS_SUBMIT.fromPDU(sp, 'test')
        self.assertEquals(p2.tp_vpf, 0)
        self.assertEquals(p2.tp_vp, None)
        self.assertEquals(p2.toPDU(), sp)

    def test_udh5(self):
        smspdu.SMS_DELIVER.determineUD(u'hello', 0, [(5, [35, 244, 0, 0])])

    def test_tp_scts(self):
        self._test_scts('011223095342+04')
    def test_tp_scts_negative(self):
        self._test_scts('011223095342-10')
    def test_tp_scts_utc(self):
        self._test_scts('01122309534200')

    def test_message_length(self):
        for n in range(22):
            for char in u'a\n':
                m = char * n
                p = smspdu.SMS_DELIVER.create('eKit', 'test', m)
                sp = p.toPDU()
                p2 = smspdu.SMS_DELIVER.fromPDU(sp, 'test')
                self.assertEquals(p2.toPDU(), sp)

    def _test_scts(self, value):
        # construct PDU
        p = smspdu.SMS_DELIVER.create('eKit', 'test', u'hellohello',
            tp_scts=value)
        self.assertEquals(p.tp_scts, value)
        sp = p.toPDU()

        # back from PDU
        p2 = smspdu.SMS_DELIVER.fromPDU(sp, 'test')
        self.assertEquals(p2.tp_scts, value)
        self.assertEquals(p2.toPDU(), sp)

    def test_ud_oddness(self):
        pdu = '000C914497423400000000112051328413001E6136FB7DBFCADFEE3354FE36A7D9E56198CD4EBBCF20F2DB5D56'
        p = smspdu.SMS_DELIVER.fromPDU(pdu, 'test')
        self.assertEquals(p.toPDU(), pdu)


class EncodingTest(unittest.TestCase):
    def _test(self, i, o):
        self.assertEqual(smspdu.attempt_encoding(i), o)

    def test_chars_in_gsm(self):
        self._test(u'héllo ñon', (u'héllo ñon', ''))

    def test_not_in_GSM_but_translatable(self):
        self._test(u'í', (u'i', ''))

    def test_chars_in_GSM_but_too_long_encoded_translate(self):
        self._test(u'x'*159 + u'\u20ac', (u'x'*159 + 'E', u''))

    def test_too_long(self):
        self._test(u'x'*161, (u'x'*160, u'x'))

    def test_utf16(self):
        s = u'أنوس مررره وحشنييي ... بسومه حبي الشريحه تبعك اشتغلت بس مو عآرفه ط'
        self._test(s, (s, u''))

class DecodingTest(unittest.TestCase):
    def _test(self, i, o, crlfok=True):
        self.assertEqual(smspdu.decode_ascii_safe(i, crlfok), o)

    def test_chars_in_gsm(self):
        self._test(u'héllo ñon', u'hllo on')

    def test_newline(self):
        self._test(u'hello\nworld', u'hello\nworld')
        self._test(u'hello\nworld', u'helloworld', False)

class DateTest(unittest.TestCase):
    def _test(self, value):
        from smspdu.pdu import unpack_date, pack_date
        self.assertEqual(unpack_date(pack_date(value)), value)
    def test_encode(self):
        self._test('011223095342+04')
    def test_encode_negative(self):
        self._test('011223095342-10')
    def test_encode_utc(self):
        self._test('01122309534200')
    def test_pack(self):
        # example 3.16 from The Book, p74
        from smspdu.pdu import pack_date
        d = map(ord, pack_date('011223095342+04'))
        self.assertEquals(d, [16, 33, 50, 144, 53, 36, 64])

if __name__ == '__main__':
    unittest.main()
