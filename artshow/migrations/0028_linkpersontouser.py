# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models
from django.conf import settings
from warnings import warn

class Migration(DataMigration):

    def forwards(self, orm):
        # This migration only applies if we're using the included peeps.Person as our Person class.
        if settings.ARTSHOW_PERSON_CLASS != "peeps.Person":
            return

        for a in orm.Artist.objects.all():
            valid_accesses = a.artistaccess_set.filter(user__email=a.person.email, can_edit=True)
            if len(valid_accesses) == 0:
                warn("Artist id %s does not have a candidate ArtistAccess attached to it" % a.artistid)
                break
            if len(valid_accesses) > 1:
                warn("Artist id %s has more than one candidate ArtistAccess. Using the first one" % a.artistid)
            a.person.user = valid_accesses[0].user
            a.save()

    def backwards(self, orm):
        "Write your backwards methods here."

    models = {
        u'artshow.agent': {
            'Meta': {'object_name': 'Agent'},
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'agent2'", 'to': u"orm['artshow.Artist']"}),
            'can_arbitrate': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'can_deliver_pieces': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'can_edit_pieces': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'can_edit_spaces': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'can_retrieve_pieces': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'agenting'", 'to': u"orm['peeps.Person']"})
        },
        u'artshow.allocation': {
            'Meta': {'unique_together': "(('artist', 'space'),)", 'object_name': 'Allocation'},
            'allocated': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '4', 'decimal_places': '1'}),
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['artshow.Artist']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'requested': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '1'}),
            'space': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['artshow.Space']"})
        },
        u'artshow.artist': {
            'Meta': {'object_name': 'Artist'},
            'agents': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'agent_for'", 'blank': 'True', 'to': u"orm['peeps.Person']"}),
            'artistid': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'attending': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'checkoffs': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['artshow.Checkoff']", 'symmetrical': 'False', 'blank': 'True'}),
            'mailback_instructions': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'mailin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'payment_to': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'receiving_payment_for'", 'null': 'True', 'to': u"orm['peeps.Person']"}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['peeps.Person']"}),
            'publicname': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'reservationdate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'spaces': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['artshow.Space']", 'through': u"orm['artshow.Allocation']", 'symmetrical': 'False'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'artshow.artistaccess': {
            'Meta': {'object_name': 'ArtistAccess'},
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['artshow.Artist']"}),
            'can_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'artshow.batchscan': {
            'Meta': {'object_name': 'BatchScan'},
            'batchtype': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'data': ('django.db.models.fields.TextField', [], {}),
            'date_scanned': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'processed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'processing_log': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'artshow.bid': {
            'Meta': {'unique_together': "(('piece', 'amount', 'invalid'),)", 'object_name': 'Bid'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '0'}),
            'bidder': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['artshow.Bidder']"}),
            'buy_now_bid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'piece': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['artshow.Piece']"})
        },
        u'artshow.bidder': {
            'Meta': {'object_name': 'Bidder'},
            'at_con_contact': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'person': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['peeps.Person']", 'unique': 'True'})
        },
        u'artshow.bidderid': {
            'Meta': {'object_name': 'BidderId'},
            'bidder': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['artshow.Bidder']"}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '8', 'primary_key': 'True'})
        },
        u'artshow.checkoff': {
            'Meta': {'object_name': 'Checkoff'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'shortname': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'artshow.chequepayment': {
            'Meta': {'object_name': 'ChequePayment', '_ormbases': [u'artshow.Payment']},
            'number': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'payee': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            u'payment_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['artshow.Payment']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'artshow.emailsignature': {
            'Meta': {'object_name': 'EmailSignature'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'signature': ('django.db.models.fields.TextField', [], {})
        },
        u'artshow.emailtemplate': {
            'Meta': {'object_name': 'EmailTemplate'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'template': ('django.db.models.fields.TextField', [], {})
        },
        u'artshow.event': {
            'Meta': {'object_name': 'Event'},
            'auto_occur': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'occurred': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'artshow.invoice': {
            'Meta': {'object_name': 'Invoice'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'paid_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'payer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['artshow.Bidder']"}),
            'tax_paid': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '7', 'decimal_places': '2', 'blank': 'True'})
        },
        u'artshow.invoiceitem': {
            'Meta': {'object_name': 'InvoiceItem'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['artshow.Invoice']"}),
            'piece': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['artshow.Piece']", 'unique': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '7', 'decimal_places': '2'})
        },
        u'artshow.invoicepayment': {
            'Meta': {'object_name': 'InvoicePayment'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '7', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['artshow.Invoice']"}),
            'notes': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'payment_method': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'artshow.payment': {
            'Meta': {'object_name': 'Payment'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '7', 'decimal_places': '2'}),
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['artshow.Artist']"}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payment_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['artshow.PaymentType']"})
        },
        u'artshow.paymenttype': {
            'Meta': {'object_name': 'PaymentType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        u'artshow.piece': {
            'Meta': {'unique_together': "(('artist', 'pieceid'),)", 'object_name': 'Piece'},
            'adult': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['artshow.Artist']"}),
            'bid_sheet_printing': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'bidsheet_scanned': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'buy_now': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '0', 'blank': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'condition': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'control_form_printing': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '8', 'blank': 'True'}),
            'media': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'min_bid': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '0', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'not_for_sale': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'other_artist': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'pieceid': ('django.db.models.fields.IntegerField', [], {}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'voice_auction': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'artshow.product': {
            'Meta': {'object_name': 'Product'},
            'adult': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['artshow.Artist']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '8', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'price': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'productid': ('django.db.models.fields.IntegerField', [], {})
        },
        u'artshow.space': {
            'Meta': {'object_name': 'Space'},
            'allow_half_spaces': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'available': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '1'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '2'}),
            'reservable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'shortname': ('django.db.models.fields.CharField', [], {'max_length': '8'})
        },
        u'artshow.task': {
            'Meta': {'object_name': 'Task'},
            'actor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'detail': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'done': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'due_at': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['artshow.Event']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'time_entered': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'peeps.person': {
            'Meta': {'object_name': 'Person'},
            'address1': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'address2': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'postcode': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'reg_id': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['auth.User']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'})
        }
    }

    complete_apps = ['artshow']
    symmetrical = True
