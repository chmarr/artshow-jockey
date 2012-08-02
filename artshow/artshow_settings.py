SPACE_FEE_PK = 3
PAYMENT_SENT_PK = 5
COMMISSION_PK = 6
SALES_PK = 7

from django.conf import settings

_globals_dict = globals()
_settings_dict = settings.__dict__
for k in _settings_dict.keys():
	if k.startswith("ARTSHOW_"):
		_globals_dict[k] = _settings_dict[k]
del _globals_dict
del _settings_dict	
