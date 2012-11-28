# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        """Convert all Artists and Bidders to peeps.Person format. If the personal details are identical,
        a new peeps.Person will be shared between Artists and/or Bidders.
        """
        Person = orm['peeps.Person']
        for OldPerson in ( orm.Artist, orm.Bidder ):
            for oldperson in OldPerson.objects.all():
                try:
                    person = Person.objects.get (
                            name=oldperson.name, address1=oldperson.address1, address2=oldperson.address2,
                            city=oldperson.city, state=oldperson.state, postcode=oldperson.postcode,
                            country=oldperson.country,
                            phone=oldperson.phone, email=oldperson.email, reg_id=oldperson.regid, comment=""
                            )
                except Person.DoesNotExist:
                    person = Person ( 
                            name=oldperson.name, address1=oldperson.address1, address2=oldperson.address2,
                            city=oldperson.city, state=oldperson.state, postcode=oldperson.postcode,
                            country=oldperson.country,
                            phone=oldperson.phone, email=oldperson.email, reg_id=oldperson.regid, comment=""
                            )
                    person.save ()
                oldperson.person = person
                oldperson.save ()

    def backwards(self, orm):
        """Convert all Artists and Bidders back to non-peeps.Person format. 
        peeps.Person objects are not deleted, but are expected to be deleted by the back migration. No biggie
        if they're not, though as the "forwards" method will find these and use them.
        """
        for OldPerson in ( orm.Artist, orm.Bidder ):
            for oldperson in OldPerson.objects.all():
                oldperson.name = oldperson.person.name
                oldperson.address1 = oldperson.person.address1
                oldperson.address2 = oldperson.person.address2
                oldperson.city = oldperson.person.city
                oldperson.state = oldperson.person.state
                oldperson.postcode = oldperson.person.postcode
                oldperson.country = oldperson.person.country
                oldperson.phone = oldperson.person.phone
                oldperson.email = oldperson.person.email
                oldperson.regid = oldperson.person.reg_id
                oldperson.person = None
                oldperson.save ()

    models = {
        'artshow.allocation': {
            'Meta': {'object_name': 'Allocation'},
            'allocated': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '1'}),
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['artshow.Artist']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'requested': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '1'}),
            'space': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['artshow.Space']"})
        },
        'artshow.artist': {
            'Meta': {'object_name': 'Artist'},
            'address1': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'address2': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'agent': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'artistid': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'checkoffs': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['artshow.Checkoff']", 'symmetrical': 'False', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'mailin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name_for_cheque': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['peeps.Person']", 'null': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'postcode': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'publicname': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'regid': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'reservationdate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'spaces': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['artshow.Space']", 'through': "orm['artshow.Allocation']", 'symmetrical': 'False'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'website': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        'artshow.artistaccess': {
            'Meta': {'object_name': 'ArtistAccess'},
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['artshow.Artist']"}),
            'can_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'artshow.batchscan': {
            'Meta': {'object_name': 'BatchScan'},
            'batchtype': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'data': ('django.db.models.fields.TextField', [], {}),
            'date_scanned': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'processed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'processing_log': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'artshow.bid': {
            'Meta': {'unique_together': "(('piece', 'amount', 'invalid'),)", 'object_name': 'Bid'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '0'}),
            'bidder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['artshow.Bidder']"}),
            'buy_now_bid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'piece': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['artshow.Piece']"})
        },
        'artshow.bidder': {
            'Meta': {'object_name': 'Bidder'},
            'address1': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'address2': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['peeps.Person']", 'null': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'postcode': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'regid': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'})
        },
        'artshow.bidderid': {
            'Meta': {'object_name': 'BidderId'},
            'bidder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['artshow.Bidder']"}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '8', 'primary_key': 'True'})
        },
        'artshow.checkoff': {
            'Meta': {'object_name': 'Checkoff'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'shortname': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'artshow.chequepayment': {
            'Meta': {'object_name': 'ChequePayment', '_ormbases': ['artshow.Payment']},
            'number': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'payee': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'payment_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['artshow.Payment']", 'unique': 'True', 'primary_key': 'True'})
        },
        'artshow.emailtemplate': {
            'Meta': {'object_name': 'EmailTemplate'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'template': ('django.db.models.fields.TextField', [], {})
        },
        'artshow.event': {
            'Meta': {'object_name': 'Event'},
            'auto_occur': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'occurred': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'artshow.invoice': {
            'Meta': {'object_name': 'Invoice'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'paid_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'payer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['artshow.Bidder']"}),
            'tax_paid': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '7', 'decimal_places': '2', 'blank': 'True'})
        },
        'artshow.invoiceitem': {
            'Meta': {'object_name': 'InvoiceItem'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['artshow.Invoice']"}),
            'piece': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['artshow.Piece']", 'unique': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '7', 'decimal_places': '2'})
        },
        'artshow.invoicepayment': {
            'Meta': {'object_name': 'InvoicePayment'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '7', 'decimal_places': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['artshow.Invoice']"}),
            'notes': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'payment_method': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'artshow.payment': {
            'Meta': {'object_name': 'Payment'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '7', 'decimal_places': '2'}),
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['artshow.Artist']"}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payment_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['artshow.PaymentType']"})
        },
        'artshow.paymenttype': {
            'Meta': {'object_name': 'PaymentType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'artshow.piece': {
            'Meta': {'object_name': 'Piece'},
            'adult': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['artshow.Artist']"}),
            'bidsheet_scanned': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'buy_now': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '0', 'blank': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '8', 'blank': 'True'}),
            'media': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'min_bid': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '0', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'not_for_sale': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'pieceid': ('django.db.models.fields.IntegerField', [], {}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'voice_auction': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'artshow.product': {
            'Meta': {'object_name': 'Product'},
            'adult': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['artshow.Artist']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '8', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'price': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'productid': ('django.db.models.fields.IntegerField', [], {})
        },
        'artshow.space': {
            'Meta': {'object_name': 'Space'},
            'available': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '2'}),
            'shortname': ('django.db.models.fields.CharField', [], {'max_length': '8'})
        },
        'artshow.task': {
            'Meta': {'object_name': 'Task'},
            'actor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'detail': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'done': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'due_at': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['artshow.Event']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'time_entered': ('django.db.models.fields.DateTimeField', [], {})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'peeps.person': {
            'Meta': {'object_name': 'Person'},
            'address1': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'address2': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'postcode': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'reg_id': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'})
        }
    }

    complete_apps = ['artshow']
    symmetrical = True
