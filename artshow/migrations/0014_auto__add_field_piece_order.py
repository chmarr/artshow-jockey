# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Piece.order'
        db.add_column('artshow_piece', 'order',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Piece.order'
        db.delete_column('artshow_piece', 'order')


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
            'agents': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'agent_for'", 'blank': 'True', 'to': "orm['peeps.Person']"}),
            'artistid': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'checkoffs': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['artshow.Checkoff']", 'symmetrical': 'False', 'blank': 'True'}),
            'mailin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'payment_to': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'receiving_payment_for'", 'null': 'True', 'to': "orm['peeps.Person']"}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['peeps.Person']"}),
            'publicname': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'reservationdate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'spaces': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['artshow.Space']", 'through': "orm['artshow.Allocation']", 'symmetrical': 'False'}),
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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'person': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['peeps.Person']", 'unique': 'True'})
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
            'Meta': {'unique_together': "(('artist', 'pieceid'),)", 'object_name': 'Piece'},
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
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'pieceid': ('django.db.models.fields.IntegerField', [], {}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
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