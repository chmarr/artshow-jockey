from django.conf import settings

def site_name ( request ):
	return {
		'SITE_NAME':settings.SITE_NAME,
		'SITE_ROOT_URL':settings.SITE_ROOT_URL,
		}
