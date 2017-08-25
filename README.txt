For documentation please "pydoc smspdu". The same documentation is available at http://pypi.python.org/pypi/smspdu

To install under Python 3:

python3 setup.py build install

-----------------------------------------------------------------------------------------------------------
  For example, if you want to send "silent SMS" or "message class 0". Flash messages are received by a mobile phone even though it has full memory. They are not stored in the phone, they just displayed on the phone display. Tested with python 3.6.2

>>> TPDCS = 0x10
>>> pdud = SMS_SUBMIT.create(' ', '0631234567', 'Hello', tp_dcs=TPDCS)
>>> pdud.toPDU()
'01000A816013325476001005C8329BFD06'

  For text Cyrillic:
>>> TPDCS = 0x18
>>> pdud = SMS_SUBMIT.create(' ', '0631234567', 'Привіт', tp_dcs=TPDCS)
>>> pdud.toPDU()
'01000A81601332547600180C041F04400438043204560442'
