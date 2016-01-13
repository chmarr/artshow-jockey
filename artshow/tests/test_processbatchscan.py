from django.utils.timezone import now

from .. import processbatchscan
from django.test import TestCase
from ..models import Person, Artist, Piece, BatchScan, Bidder, BidderId, Bid


def create_and_process_batch(batchtype, data):
    batch = BatchScan.objects.create(batchtype=batchtype, data=data, date_scanned=now())
    processbatchscan.process_batchscan(batch.id)
    batch = BatchScan.objects.get(id=batch.id)
    return batch


class BatchScanTestCase(TestCase):

    def assertProcessingError(self, batch, message):
        self.assertEqual(batch.processed, False)
        self.assertIn(message, batch.processing_log)

    def assertProcessingComplete(self, batch):
        self.assertEqual(batch.processed, True)
        self.assertIn('Processing Complete', batch.processing_log)


class BidScanTest(BatchScanTestCase):

    @classmethod
    def setUpClass(cls):
        cls.person1 = Person.objects.create(name="John Smith")
        cls.person2 = Person.objects.create(name="Joe Diddly")
        cls.artist1 = Artist.objects.create(artistid=1, person=cls.person1, publicname="Da Artiste")
        cls.piece_nobuynow = Piece.objects.create(artist=cls.artist1, pieceid=1, name="First Piece", min_bid=10, status=Piece.StatusInShow)
        cls.piece_bynow = Piece.objects.create(artist=cls.artist1, pieceid=2, name="Second Piece", min_bid=10,
                                               buy_now=15, status=Piece.StatusInShow)
        cls.piece_nfs = Piece.objects.create(artist=cls.artist1, pieceid=3, name="Third Piece", not_for_sale=True, status=Piece.StatusInShow)
        cls.piece_notinshow = Piece.objects.create(artist=cls.artist1, pieceid=4, name="Fourth Piece", min_bid=10)
        cls.bidder = Bidder.objects.create(person=cls.person2)
        BidderId.objects.create(id='1001', bidder=cls.bidder)

        cls.piece_withabid = Piece.objects.create(artist=cls.artist1, pieceid=5, name="Fifth Piece", min_bid=10, status=Piece.StatusInShow)
        Bid.objects.create(piece=cls.piece_withabid, bidder=cls.bidder, amount=15)

        cls.piece_withabuynow = Piece.objects.create(artist=cls.artist1, pieceid=6, name="Sixth Piece", min_bid=10,
                                                     buy_now=15, status=Piece.StatusInShow)
        Bid.objects.create(piece=cls.piece_withabuynow, bidder=cls.bidder, amount=15, buy_now_bid=True)

        cls.piece_won = Piece.objects.create(artist=cls.artist1, pieceid=7, name="Seventh Piece", min_bid=10,
                                                     buy_now=15, status=Piece.StatusWon)
        Bid.objects.create(piece=cls.piece_won, bidder=cls.bidder, amount=15, buy_now_bid=True)


    def assertNoBids(self, piece):
        with self.assertRaises(Bid.DoesNotExist):
            bid = piece.top_bid()

    def test_intermediate_no_bids(self):
        batch = create_and_process_batch(2, "A1P1\nNB\n")
        self.assertProcessingComplete(batch)

        piece = Piece.objects.get(id=self.piece_nobuynow.id)
        self.assertNoBids(piece)
        self.assertEqual(piece.status, piece.StatusInShow)

    def test_intermediate_normal_bid(self):
        batch = create_and_process_batch(2, "A1P1\nB1001\n10\nNS\n")
        self.assertProcessingComplete(batch)

        piece = Piece.objects.get(id=self.piece_nobuynow.id)
        top_bid = piece.top_bid()
        self.assertEqual(top_bid.amount, 10)
        self.assertEqual(top_bid.bidder, self.bidder)
        self.assertEqual(piece.status, piece.StatusInShow)

    def test_intermediate_over_bid(self):
        batch = create_and_process_batch(2, "A1P5\nB1001\n25\nNS\n")
        self.assertProcessingComplete(batch)

        piece = Piece.objects.get(id=self.piece_withabid.id)
        top_bid = piece.top_bid()
        self.assertEqual(top_bid.amount, 25)
        self.assertEqual(top_bid.bidder, self.bidder)
        self.assertEqual(piece.status, piece.StatusInShow)
        self.assertEqual(piece.bid_set.count(), 2)

    def test_intermediate_buynow_bid(self):
        batch = create_and_process_batch(2, "A1P2\nB1001\n15\nNBN\n")
        self.assertProcessingComplete(batch)

        piece = Piece.objects.get(id=self.piece_bynow.id)
        top_bid = piece.top_bid()
        self.assertEqual(top_bid.amount, 15)
        self.assertEqual(top_bid.bidder, self.bidder)
        self.assertEqual(top_bid.buy_now_bid, True)
        self.assertEqual(piece.status, piece.StatusInShow)

    def test_intermediate_toauction_bid(self):
        batch = create_and_process_batch(2, "A1P1\nB1001\n1500\nNAS\n")
        self.assertProcessingComplete(batch)

        piece = Piece.objects.get(id=self.piece_nobuynow.id)
        top_bid = piece.top_bid()
        self.assertEqual(top_bid.amount, 1500)
        self.assertEqual(top_bid.bidder, self.bidder)
        self.assertEqual(piece.status, piece.StatusInShow)
        self.assertEqual(piece.voice_auction, True)

    def test_intermediate_nfs(self):
        batch = create_and_process_batch(2, "A1P3\nNFS\n")
        self.assertProcessingComplete(batch)

        piece = Piece.objects.get(id=self.piece_nfs.id)
        self.assertNoBids(piece)
        self.assertEqual(piece.status, piece.StatusInShow)

    def test_atclose_no_bids(self):
        batch = create_and_process_batch(3, "A1P1\nNB\n")
        self.assertProcessingComplete(batch)

        piece = Piece.objects.get(id=self.piece_nobuynow.id)
        self.assertNoBids(piece)
        self.assertEqual(piece.status, piece.StatusInShow)
        self.assertEqual(piece.bidsheet_scanned, True)

    def test_atclose_normal_bid(self):
        batch = create_and_process_batch(3, "A1P1\nB1001\n10\nNS\n")
        self.assertProcessingComplete(batch)

        piece = Piece.objects.get(id=self.piece_nobuynow.id)
        top_bid = piece.top_bid()
        self.assertEqual(top_bid.amount, 10)
        self.assertEqual(top_bid.bidder, self.bidder)
        self.assertEqual(piece.status, piece.StatusWon)
        self.assertEqual(piece.bidsheet_scanned, True)

    def test_atclose_over_bid(self):
        batch = create_and_process_batch(3, "A1P5\nB1001\n25\nNS\n")
        self.assertProcessingComplete(batch)

        piece = Piece.objects.get(id=self.piece_withabid.id)
        top_bid = piece.top_bid()
        self.assertEqual(top_bid.amount, 25)
        self.assertEqual(top_bid.bidder, self.bidder)
        self.assertEqual(piece.status, piece.StatusWon)
        self.assertEqual(piece.bidsheet_scanned, True)
        self.assertEqual(piece.bid_set.count(), 2)

    def test_atclose_buynow_bid(self):
        batch = create_and_process_batch(3, "A1P2\nB1001\n15\nNBN\n")
        self.assertProcessingComplete(batch)

        piece = Piece.objects.get(id=self.piece_bynow.id)
        top_bid = piece.top_bid()
        self.assertEqual(top_bid.amount, 15)
        self.assertEqual(top_bid.bidder, self.bidder)
        self.assertEqual(top_bid.buy_now_bid, True)
        self.assertEqual(piece.status, piece.StatusWon)
        self.assertEqual(piece.bidsheet_scanned, True)

    def test_atclose_toauction_bid(self):
        batch = create_and_process_batch(3, "A1P1\nB1001\n1500\nNAS\n")
        self.assertProcessingComplete(batch)

        piece = Piece.objects.get(id=self.piece_nobuynow.id)
        top_bid = piece.top_bid()
        self.assertEqual(top_bid.amount, 1500)
        self.assertEqual(top_bid.bidder, self.bidder)
        self.assertEqual(piece.status, piece.StatusInShow)
        self.assertEqual(piece.voice_auction, True)
        self.assertEqual(piece.bidsheet_scanned, True)

    def test_atclose_nfs(self):
        batch = create_and_process_batch(3, "A1P3\nNFS\n")
        self.assertProcessingComplete(batch)

        piece = Piece.objects.get(id=self.piece_nfs.id)
        self.assertNoBids(piece)
        self.assertEqual(piece.status, piece.StatusInShow)
        self.assertEqual(piece.bidsheet_scanned, True)

    def test_insufficient_bid(self):
        batch = create_and_process_batch(2, "A1P1\nB1001\n5\nNS\n")
        self.assertProcessingError(batch, 'Bid cannot be less than Min Bid')

        piece = Piece.objects.get(id=self.piece_nobuynow.id)
        self.assertNoBids(piece)
        self.assertEqual(piece.status, piece.StatusInShow)

    def test_notinshow(self):
        batch = create_and_process_batch(2, "A1P4\nB1001\n5\nNS\n")
        self.assertProcessingError(batch, 'New bids cannot be placed on pieces that are not In Show')

        piece = Piece.objects.get(id=self.piece_notinshow.id)
        self.assertNoBids(piece)
        self.assertEqual(piece.status, piece.StatusNotInShow)

    def test_already_won(self):
        batch = create_and_process_batch(2, "A1P7\nB1001\n5\nNS\n")
        self.assertProcessingError(batch, 'New bids cannot be placed on pieces that are not In Show')

        piece = Piece.objects.get(id=self.piece_won.id)
        top_bid = piece.top_bid()
        self.assertEqual(top_bid.amount, 15)
        self.assertEqual(top_bid.bidder, self.bidder)
        self.assertEqual(piece.status, piece.StatusWon)

    def test_not_buynow(self):
        batch = create_and_process_batch(2, "A1P1\nB1001\n15\nNBN\n")
        self.assertProcessingError(batch, 'Buy Now option not available on this piece')

        piece = Piece.objects.get(id=self.piece_nobuynow.id)
        self.assertNoBids(piece)
        self.assertEqual(piece.status, piece.StatusInShow)

    def test_insufficient_outbid(self):
        batch = create_and_process_batch(2, "A1P5\nB1001\n10\nNS\n")
        self.assertProcessingError(batch, 'New bid must be higher than existing bids')

        piece = Piece.objects.get(id=self.piece_withabid.id)
        top_bid = piece.top_bid()
        self.assertEqual(top_bid.amount, 15)
        self.assertEqual(top_bid.bidder, self.bidder)
        self.assertEqual(piece.status, piece.StatusInShow)

    def test_insufficient_buynow(self):
        batch = create_and_process_batch(2, "A1P2\nB1001\n10\nNBN\n")
        self.assertProcessingError(batch, 'Buy Now bid cannot be less than Buy Now price')

        piece = Piece.objects.get(id=self.piece_bynow.id)
        self.assertNoBids(piece)
        self.assertEqual(piece.status, piece.StatusInShow)

    def test_insufficient_auction_outbid(self):
        batch = create_and_process_batch(2, "A1P5\nB1001\n10\nNAS\n")
        self.assertProcessingError(batch, 'New bid must be higher than existing bids')

        piece = Piece.objects.get(id=self.piece_withabid.id)
        top_bid = piece.top_bid()
        self.assertEqual(top_bid.amount, 15)
        self.assertEqual(top_bid.bidder, self.bidder)
        self.assertEqual(piece.status, piece.StatusInShow)

    def test_same_bid(self):
        batch = create_and_process_batch(2, "A1P5\nB1001\n15\nNS\n")
        self.assertProcessingComplete(batch)

        piece = Piece.objects.get(id=self.piece_withabid.id)
        top_bid = piece.top_bid()
        self.assertEqual(top_bid.amount, 15)
        self.assertEqual(top_bid.bidder, self.bidder)
        self.assertEqual(piece.status, piece.StatusInShow)

    def test_same_bid_switch_to_buynow(self):
        batch = create_and_process_batch(2, "A1P5\nB1001\n15\nNBN\n")
        self.assertProcessingError(batch, 'New bid must be higher than existing bids')

        piece = Piece.objects.get(id=self.piece_withabid.id)
        top_bid = piece.top_bid()
        self.assertEqual(top_bid.amount, 15)
        self.assertEqual(top_bid.bidder, self.bidder)
        self.assertEqual(top_bid.buy_now_bid, False)
        self.assertEqual(piece.status, piece.StatusInShow)

    def test_already_buynow(self):
        batch = create_and_process_batch(2, "A1P6\nB1001\n30\nNS\n")
        self.assertProcessingError(batch, 'Cannot bid on piece that has had Buy Now option invoked')

        piece = Piece.objects.get(id=self.piece_withabuynow.id)
        top_bid = piece.top_bid()
        self.assertEqual(top_bid.amount, 15)
        self.assertEqual(top_bid.bidder, self.bidder)
        self.assertEqual(piece.status, piece.StatusInShow)

    def test_bid_on_nfs(self):
        batch = create_and_process_batch(2, "A1P3\nB1001\n30\nNS\n")
        self.assertProcessingError(batch, 'Not For Sale piece cannot have bids placed on it')

        piece = Piece.objects.get(id=self.piece_nfs.id)
        self.assertNoBids(piece)
        self.assertEqual(piece.status, piece.StatusInShow)

    def test_buy_now_on_piece_with_bids(self):
        batch = create_and_process_batch(2, "A1P5\nB1001\n30\nNBN\n")
        self.assertProcessingError(batch, 'Buy Now option not available on piece with bids')

        piece = Piece.objects.get(id=self.piece_withabid.id)
        top_bid = piece.top_bid()
        self.assertEqual(top_bid.amount, 15)
        self.assertEqual(top_bid.bidder, self.bidder)
        self.assertEqual(piece.status, piece.StatusInShow)

    def test_piece_does_not_exist(self):
        batch = create_and_process_batch(2, "A99P99\nB1001\n15\nNS\n")
        self.assertProcessingError(batch, 'piece does not exist')

    def test_bidder_does_not_exist(self):
        batch = create_and_process_batch(2, "A1P1\nB9999\n15\nNS\n")
        self.assertProcessingError(batch, 'bidder does not exist')

    def test_comments_stripped(self):
        batch = create_and_process_batch(2, "A1P1\nB1001 # this is a comment\n10\nNS\n")
        self.assertProcessingComplete(batch)

    def test_bare_ns(self):
        batch = create_and_process_batch(2, "NS\n")
        self.assertProcessingComplete(batch)

    def test_missing_bidder(self):
        batch = create_and_process_batch(2, "A1P1\n1234\nNS",)
        self.assertProcessingError(batch, 'found price not immediately after bidder')

    def test_missing_price_ns(self):
        batch = create_and_process_batch(2, "A1P1\nB1001\nNS")
        self.assertProcessingError(batch, 'normal sale scan found not immediately after price')

    def test_missing_price_buynow(self):
        batch = create_and_process_batch(2, "A1P1\nB1001\nNBN")
        self.assertProcessingError(batch, 'buy now scan found not immediately after price')

    def test_missing_price_toauction(self):
        batch = create_and_process_batch(2, "A1P1\nB1001\nNAS")
        self.assertProcessingError(batch, 'auction sale scan found not immediately after price')

    def test_blanks(self):
        batch = create_and_process_batch(2, "A1P1\n B1001 \n\n10\nNS\n")
        self.assertProcessingComplete(batch)

    def test_incomplete_block(self):
        batch = create_and_process_batch(2, "A1P2")
        self.assertProcessingError(batch, 'block incomplete')

    def test_incomplete_previous_block(self):
        batch = create_and_process_batch(2, "A1P2\nB1001\nA1P2\nNB")
        self.assertProcessingError(batch, 'previous block incomplete')

    def test_stray_bidder(self):
        batch = create_and_process_batch(2, "B1001\n")
        self.assertProcessingError(batch, 'found bidder scan not immediately after piece')

    def test_stray_nfs(self):
        batch = create_and_process_batch(2, "NFS\n")
        self.assertProcessingError(batch, 'not for sale scan found not immediately after piece')

    def test_stray_nobids(self):
        batch = create_and_process_batch(2, "NB\n")
        self.assertProcessingError(batch, 'no bids scan found not immediately after piece')

    def test_improper_nfs(self):
        batch = create_and_process_batch(2, "A1P1\nNFS\n")
        self.assertProcessingError(batch, 'Not for sale found on non NFS piece')

    def test_nobids_bid_piece(self):
        batch = create_and_process_batch(2, "A1P5\nNB\n")
        self.assertProcessingError(batch, 'No Bid found for pieces with bids')

    def test_unknown_line(self):
        batch = create_and_process_batch(2, "WTF\n")
        self.assertProcessingError(batch, 'unknown line')


class LocationScanTest(BatchScanTestCase):

    @classmethod
    def setUpClass(cls):
        cls.person1 = Person.objects.create(name="Chris Wilkie")
        cls.artist2 = Artist.objects.create(artistid=2, person=cls.person1, publicname="Man with the Planner")
        cls.piece1 = Piece.objects.create(artist=cls.artist2, pieceid=1, name="First Piece", min_bid=10,
                                          status=Piece.StatusNotInShow)
        cls.piece2 = Piece.objects.create(artist=cls.artist2, pieceid=2, name="Second Piece", min_bid=10,
                                          status=Piece.StatusNotInShowLocked)
        cls.piece3 = Piece.objects.create(artist=cls.artist2, pieceid=3, name="Third Piece", min_bid=10,
                                          status=Piece.StatusSold)


    def test_locate_notinshow(self):
        batch = create_and_process_batch(1, data="LA1\nA2P1\nLEND\n")
        self.assertProcessingComplete(batch)

        piece = Piece.objects.get(id=self.piece1.id)
        self.assertEqual(piece.status, piece.StatusInShow)

    def test_locate_notinshowlocked(self):
        batch = create_and_process_batch(1, data="LA1\nA2P2\nLEND\n")
        self.assertProcessingComplete(batch)

        piece = Piece.objects.get(id=self.piece2.id)
        self.assertEqual(piece.status, piece.StatusInShow)

    def test_locate_notinshowsold(self):
        batch = create_and_process_batch(1, data="LA1\nA2P3\nLEND\n")
        self.assertProcessingComplete(batch)

        piece = Piece.objects.get(id=self.piece3.id)
        self.assertEqual(piece.status, piece.StatusSold)

    def test_piece_not_found(self):
        batch = create_and_process_batch(1, data="LA1\nA99P99\nLEND\n")
        self.assertProcessingError(batch, 'piece does not exist')

    def test_no_location(self):
        batch = create_and_process_batch(1, data="A99P99\nLEND\n")
        self.assertProcessingError(batch, 'piece not found immediately after location')
        self.assertProcessingError(batch, 'location block ended without being begun')

    def test_no_end(self):
        batch = create_and_process_batch(1, data="LA1\nA2P1\n")
        self.assertProcessingError(batch, 'last block missing END')

    def test_stray_end(self):
        batch = create_and_process_batch(1, data="LEND\n")
        self.assertProcessingError(batch, 'location block ended without being begun')

    def test_comments_stripped(self):
        batch = create_and_process_batch(1, "LA1\nA2P1 # This is a comment\nLEND\n")
        self.assertProcessingComplete(batch)

    def test_blanks(self):
        batch = create_and_process_batch(1, "LA1\n A2P1 \n\nLEND\n")
        self.assertProcessingComplete(batch)


class BidderIDScanTest(BatchScanTestCase):

    @classmethod
    def setUpClass(cls):
        cls.person1 = Person.objects.create(name="Fred Staring")
        cls.bidder = Bidder.objects.create(person=cls.person1)
        BidderId.objects.create(id='2002', bidder=cls.bidder)

        cls.person2 = Person.objects.create(name="I.P.Freely")

    def test_enter_bidder(self):
        batch = create_and_process_batch(4, "P%d\nB4004\n" % self.person2.id)
        self.assertProcessingComplete(batch)

        bidder = Bidder.objects.get(bidderid__id="4004")
        self.assertEqual(bidder.person, self.person2)

    def test_additional_bidder_id(self):
        batch = create_and_process_batch(4, "P%d\nB4012\n" % self.person1.id)
        self.assertProcessingComplete(batch)

        bidder = Bidder.objects.get(bidderid__id="4012")
        self.assertEqual(bidder.person, self.person1)

        self.assertEqual(bidder.bidderid_set.count(), 2)

    def test_missing_person_id(self):
        batch = create_and_process_batch(4, "B4012\n")
        self.assertProcessingError(batch, 'unexpected bidder id')

    def test_missing_bidder_id(self):
        batch = create_and_process_batch(4, "P%d\n" % self.person1.id)
        self.assertProcessingError(batch, 'block incomplete')

    def test_person_not_found(self):
        batch = create_and_process_batch(4, "P9999\nB4004\n")
        self.assertProcessingError(batch, 'person not found')

    def test_reused_bidder_id(self):
        batch = create_and_process_batch(4, "P%d\nB2002" % self.person1.id)
        self.assertProcessingError(batch, 'bidder id already exists')

    def test_comments_stripped(self):
        batch = create_and_process_batch(4, "P%d # this is a comment\nB4004\n" % self.person2.id)
        self.assertProcessingComplete(batch)

    def test_blanks(self):
        batch = create_and_process_batch(4, "P%d \n\nB4004  \n" % self.person2.id)
        self.assertProcessingComplete(batch)
