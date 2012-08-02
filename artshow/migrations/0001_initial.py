# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Space'
        db.create_table('artshow_space', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('shortname', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('available', self.gf('django.db.models.fields.DecimalField')(max_digits=4, decimal_places=1)),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=4, decimal_places=2)),
        ))
        db.send_create_signal('artshow', ['Space'])

        # Adding model 'Checkoff'
        db.create_table('artshow_checkoff', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('shortname', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('artshow', ['Checkoff'])

        # Adding model 'Artist'
        db.create_table('artshow_artist', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('address1', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('address2', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('postcode', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('regid', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('artistid', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('publicname', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('mailin', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('agent', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('reservationdate', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('name_for_cheque', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
        ))
        db.send_create_signal('artshow', ['Artist'])

        # Adding M2M table for field checkoffs on 'Artist'
        db.create_table('artshow_artist_checkoffs', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('artist', models.ForeignKey(orm['artshow.artist'], null=False)),
            ('checkoff', models.ForeignKey(orm['artshow.checkoff'], null=False))
        ))
        db.create_unique('artshow_artist_checkoffs', ['artist_id', 'checkoff_id'])

        # Adding model 'Allocation'
        db.create_table('artshow_allocation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('artist', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['artshow.Artist'])),
            ('space', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['artshow.Space'])),
            ('requested', self.gf('django.db.models.fields.DecimalField')(max_digits=4, decimal_places=1)),
            ('allocated', self.gf('django.db.models.fields.DecimalField')(max_digits=4, decimal_places=1)),
        ))
        db.send_create_signal('artshow', ['Allocation'])

        # Adding model 'Bidder'
        db.create_table('artshow_bidder', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('address1', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('address2', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('postcode', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('regid', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('artshow', ['Bidder'])

        # Adding model 'BidderId'
        db.create_table('artshow_bidderid', (
            ('id', self.gf('django.db.models.fields.CharField')(max_length=8, primary_key=True)),
            ('bidder', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['artshow.Bidder'])),
        ))
        db.send_create_signal('artshow', ['BidderId'])

        # Adding model 'Piece'
        db.create_table('artshow_piece', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('artist', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['artshow.Artist'])),
            ('pieceid', self.gf('django.db.models.fields.IntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=8, blank=True)),
            ('not_for_sale', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('adult', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('min_bid', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=5, decimal_places=0, blank=True)),
            ('buy_now', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=5, decimal_places=0, blank=True)),
            ('voice_auction', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('bidsheet_scanned', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('artshow', ['Piece'])

        # Adding model 'Product'
        db.create_table('artshow_product', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('artist', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['artshow.Artist'])),
            ('productid', self.gf('django.db.models.fields.IntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=8, blank=True)),
            ('adult', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('price', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=5, decimal_places=2, blank=True)),
        ))
        db.send_create_signal('artshow', ['Product'])

        # Adding model 'Bid'
        db.create_table('artshow_bid', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bidder', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['artshow.Bidder'])),
            ('amount', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=0)),
            ('piece', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['artshow.Piece'])),
            ('buy_now_bid', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('invalid', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('artshow', ['Bid'])

        # Adding unique constraint on 'Bid', fields ['piece', 'amount', 'invalid']
        db.create_unique('artshow_bid', ['piece_id', 'amount', 'invalid'])

        # Adding model 'EmailTemplate'
        db.create_table('artshow_emailtemplate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('template', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('artshow', ['EmailTemplate'])

        # Adding model 'PaymentType'
        db.create_table('artshow_paymenttype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40)),
        ))
        db.send_create_signal('artshow', ['PaymentType'])

        # Adding model 'Payment'
        db.create_table('artshow_payment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('artist', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['artshow.Artist'])),
            ('amount', self.gf('django.db.models.fields.DecimalField')(max_digits=7, decimal_places=2)),
            ('payment_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['artshow.PaymentType'])),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('date', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal('artshow', ['Payment'])

        # Adding model 'Invoice'
        db.create_table('artshow_invoice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('payer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['artshow.Bidder'])),
            ('tax_paid', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=7, decimal_places=2, blank=True)),
            ('total_paid', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=7, decimal_places=2, blank=True)),
            ('paid_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('payment_method', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('artshow', ['Invoice'])

        # Adding model 'InvoiceItem'
        db.create_table('artshow_invoiceitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('piece', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['artshow.Piece'], unique=True)),
            ('invoice', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['artshow.Invoice'])),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=7, decimal_places=2)),
        ))
        db.send_create_signal('artshow', ['InvoiceItem'])

        # Adding model 'BatchScan'
        db.create_table('artshow_batchscan', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('batchtype', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('data', self.gf('django.db.models.fields.TextField')()),
            ('date_scanned', self.gf('django.db.models.fields.DateTimeField')()),
            ('processed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('processing_log', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('artshow', ['BatchScan'])

        # Adding model 'Event'
        db.create_table('artshow_event', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('occurred', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('auto_occur', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('artshow', ['Event'])

        # Adding model 'Task'
        db.create_table('artshow_task', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('summary', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('detail', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('time_entered', self.gf('django.db.models.fields.DateTimeField')()),
            ('due_at', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['artshow.Event'])),
            ('actor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('done', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('artshow', ['Task'])

        # Adding model 'ArtistAccess'
        db.create_table('artshow_artistaccess', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('artist', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['artshow.Artist'])),
            ('can_edit', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('artshow', ['ArtistAccess'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Bid', fields ['piece', 'amount', 'invalid']
        db.delete_unique('artshow_bid', ['piece_id', 'amount', 'invalid'])

        # Deleting model 'Space'
        db.delete_table('artshow_space')

        # Deleting model 'Checkoff'
        db.delete_table('artshow_checkoff')

        # Deleting model 'Artist'
        db.delete_table('artshow_artist')

        # Removing M2M table for field checkoffs on 'Artist'
        db.delete_table('artshow_artist_checkoffs')

        # Deleting model 'Allocation'
        db.delete_table('artshow_allocation')

        # Deleting model 'Bidder'
        db.delete_table('artshow_bidder')

        # Deleting model 'BidderId'
        db.delete_table('artshow_bidderid')

        # Deleting model 'Piece'
        db.delete_table('artshow_piece')

        # Deleting model 'Product'
        db.delete_table('artshow_product')

        # Deleting model 'Bid'
        db.delete_table('artshow_bid')

        # Deleting model 'EmailTemplate'
        db.delete_table('artshow_emailtemplate')

        # Deleting model 'PaymentType'
        db.delete_table('artshow_paymenttype')

        # Deleting model 'Payment'
        db.delete_table('artshow_payment')

        # Deleting model 'Invoice'
        db.delete_table('artshow_invoice')

        # Deleting model 'InvoiceItem'
        db.delete_table('artshow_invoiceitem')

        # Deleting model 'BatchScan'
        db.delete_table('artshow_batchscan')

        # Deleting model 'Event'
        db.delete_table('artshow_event')

        # Deleting model 'Task'
        db.delete_table('artshow_task')

        # Deleting model 'ArtistAccess'
        db.delete_table('artshow_artistaccess')


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
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'postcode': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'publicname': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'regid': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'reservationdate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'spaces': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['artshow.Space']", 'through': "orm['artshow.Allocation']", 'symmetrical': 'False'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'})
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
            'payment_method': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'tax_paid': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '7', 'decimal_places': '2', 'blank': 'True'}),
            'total_paid': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '7', 'decimal_places': '2', 'blank': 'True'})
        },
        'artshow.invoiceitem': {
            'Meta': {'object_name': 'InvoiceItem'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['artshow.Invoice']"}),
            'piece': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['artshow.Piece']", 'unique': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '7', 'decimal_places': '2'})
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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '8', 'blank': 'True'}),
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
        }
    }

    complete_apps = ['artshow']
