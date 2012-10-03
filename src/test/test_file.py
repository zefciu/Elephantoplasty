try:
    import unittest2 as unittest
except ImportError:
    import unittest

try:
    import webtest
except ImportError:
    webtest = None

import os
from psycopg2 import OperationalError, ProgrammingError

import eplasty as ep

from .util import get_test_conn

CONTENT_PARROT = """
A customer enters a pet shop.
Mr. Praline: 'Ello, I wish to register a complaint.
(The owner does not respond.)
Mr. Praline: 'Ello, Miss?
Owner: What do you mean "miss"?
Mr. Praline: I'm sorry, I have a cold. I wish to make a complaint!
Owner: We're closin' for lunch.
Mr. Praline: Never mind that, my lad. I wish to complain about this parrot what I purchased not half an hour ago from this very boutique.
Owner: Oh yes, the, uh, the Norwegian Blue...What's,uh...What's wrong with it?
Mr. Praline: I'll tell you what's wrong with it, my lad. 'E's dead, that's what's wrong with it!
Owner: No, no, 'e's uh,...he's resting.
Mr. Praline: Look, matey, I know a dead parrot when I see one, and I'm looking at one right now.
Owner: No no he's not dead, he's, he's restin'! Remarkable bird, the Norwegian Blue, idn'it, ay? Beautiful plumage!
Mr. Praline: The plumage don't enter into it. It's stone dead.
Owner: Nononono, no, no! 'E's resting!
Mr. Praline: All right then, if he's restin', I'll wake him up! (shouting at the cage) 'Ello, Mister Polly Parrot! I've got a lovely fresh cuttle fish for you if you
show...
(owner hits the cage)
Owner: There, he moved!
Mr. Praline: No, he didn't, that was you hitting the cage!
Owner: I never!!
Mr. Praline: Yes, you did!
Owner: I never, never did anything...
Mr. Praline: (yelling and hitting the cage repeatedly) 'ELLO POLLY!!!!! Testing! Testing! Testing! Testing! This is your nine o'clock alarm call!
(Takes parrot out of the cage and thumps its head on the counter. Throws it up in the air and watches it plummet to the floor.)
Mr. Praline: Now that's what I call a dead parrot.
Owner: No, no.....No, 'e's stunned!
Mr. Praline: STUNNED?!?
Owner: Yeah! You stunned him, just as he was wakin' up! Norwegian Blues stun easily, major.
Mr. Praline: Um...now look...now look, mate, I've definitely 'ad enough of this. That parrot is definitely deceased, and when I purchased it not 'alf an hour
ago, you assured me that its total lack of movement was due to it bein' tired and shagged out following a prolonged squawk.
Owner: Well, he's...he's, ah...probably pining for the fjords.
Mr. Praline: PININ' for the FJORDS?!?!?!? What kind of talk is that?, look, why did he fall flat on his back the moment I got 'im home?
Owner: The Norwegian Blue prefers keepin' on it's back! Remarkable bird, id'nit, squire? Lovely plumage!
Mr. Praline: Look, I took the liberty of examining that parrot when I got it home, and I discovered the only reason that it had been sitting on its perch in the
first place was that it had been NAILED there.
(pause)
Owner: Well, o'course it was nailed there! If I hadn't nailed that bird down, it would have nuzzled up to those bars, bent 'em apart with its beak, and
VOOM! Feeweeweewee!
Mr. Praline: "VOOM"?!? Mate, this bird wouldn't "voom" if you put four million volts through it! 'E's bleedin' demised!
Owner: No no! 'E's pining!
Mr. Praline: 'E's not pinin'! 'E's passed on! This parrot is no more! He has ceased to be! 'E's expired and gone to meet 'is maker! 'E's a stiff! Bereft of life, 'e
rests in peace! If you hadn't nailed 'im to the perch 'e'd be pushing up the daisies! 'Is metabolic processes are now 'istory! 'E's off the twig! 'E's kicked the
bucket, 'e's shuffled off 'is mortal coil, run down the curtain and joined the bleedin' choir invisibile!! THIS IS AN EX-PARROT!!
(pause)
Owner: Well, I'd better replace it, then. (he takes a quick peek behind the counter) Sorry squire, I've had a look 'round the back of the shop, and uh,
we're right out of parrots.
Mr. Praline: I see. I see, I get the picture.
Owner: I got a slug.
(pause)
Mr. Praline: Pray, does it talk?
Owner: Nnnnot really.
Mr. Praline: WELL IT'S HARDLY A BLOODY REPLACEMENT, IS IT?!!???!!?
Owner: N-no, I guess not. (gets ashamed, looks at his feet)
Mr. Praline: Well.
(pause)
Owner: (quietly) D'you.... d'you want to come back to my place?
Mr. Praline: (looks around) Yeah, all right, sure.
"""

CONTENT_HUNGARIAN = """
(Set: A tobacconist's shop.)
Text on screen: In 1970, the British Empire lay in ruins, and foreign nationalists frequented the streets - many of them Hungarians (not the streets - the foreign nationals). Anyway, many of these Hungarians went into tobacconist's shops to buy cigarettes....
A Hungarian tourist approaches the clerk. The tourist is reading haltingly from a phrase book.
Hungarian: I will not buy this record, it is scratched.
Clerk: Sorry?
Hungarian: I will not buy this record, it is scratched.
Clerk: Uh, no, no, no. This is a tobacconist's.
Hungarian: Ah! I will not buy this *tobacconist's*, it is scratched.
Clerk: No, no, no, no. Tobacco...um...cigarettes (holds up a pack).
Hungarian: Ya! See-gar-ets! Ya! Uh...My hovercraft is full of eels.
Clerk: Sorry?
Hungarian: My hovercraft (pantomimes puffing a cigarette)...is full of eels
(pretends to strike a match).
Clerk: Ahh, matches!
Hungarian: Ya! Ya! Ya! Ya! Do you waaaaant...do you waaaaaant...to come back to my place, bouncy bouncy?
Clerk: Here, I don't think you're using that thing right.
Hungarian: You great poof.
Clerk: That'll be six and six, please.
Hungarian: If I said you had a beautiful body, would you hold it against me? I...I am no longer infected.
Clerk: Uh, may I, uh...(takes phrase book, flips through it)...Costs six and six...ah, here we are. (speaks weird Hungarian-sounding words)
Hungarian punches the clerk.
Meanwhile, a policeman on a quiet street cups his ear as if hearing a cry of distress. He sprints for many blocks and finally enters the tobacconist's.
Cop: What's going on here then?
Hungarian: Ah. You have beautiful thighs.
Cop: (looks down at himself) WHAT?!?
Clerk: He hit me!
Hungarian: Drop your panties, Sir William; I cannot wait 'til lunchtime. (points at clerk)
Cop: RIGHT!!! (drags Hungarian away by the arm)
Hungarian: (indignantly) My nipples explode with delight!
(scene switches to a courtroom. Characters are all in powdered wigs and judicial robes, except publisher and cop.
Cast:
    Judge: Terry Jones 
    Bailiff: Eric Idle 
    Lawyer: John Cleese 
    Cop: Graham (still) 
    Publisher: Michael Palin 
Bailiff: Call Alexander Yalt!
(voices sing out the name several times)
Judge: Oh, shut up!
Bailiff: (to publisher) You are Alexander Yalt?
Publisher: (in a sing-songy voice) Oh, I am.
Bailiff: Skip the impersonations. You are Alexander Yalt?
Publisher: I am.
Bailiff: You are hereby charged that on the 28th day of May, 1970, you did willfully, unlawfully, and with malice aforethought, publish an alleged English-Hungarian phrase book with intent to cause a breach of the peace. How do you plead?
Publisher: Not guilty.
Bailiff: You live at 46 Horton Terrace?
Publisher: I do live at 46 Horton terrace.
Bailiff: You are the director of a publishing company?
Publisher: I am the director of a publishing company.
Bailiff: Your company publishes phrase books?
Publisher: My company does publish phrase books.
Bailiff: You did say 46 Horton Terrace, did you?
Publisher: Yes.
Bailiff: (strikes a gong) Ah! Got him!
(lawyer and cop applaud, laugh)
Judge: Get on with it, get on with it.
Bailiff: That's fine. On the 28th of May, you published this phrase book.
Publisher: I did.
Bailiff: I quote one example. The Hungarian phrase meaning "Can you direct me to the station?" is translated by the English phrase, "Please fondle my bum."
Publisher: I wish to plead incompetence.
Cop: (stands) Please may I ask for an adjournment, m'lord?
Judge: An adjournment? Certainly not!
(the cop sits down again, emitting perhaps the longest and loudest release of bodily gas in the history of the universe.)
Judge: Why on earth didn't you say WHY you wanted an adjournment?
Cop: I didn't know an acceptable legal phrase, m'lord.
(cut to ancient footage of old women applauding)
Judge: (banging + swinging gavel) If there's any more stock film of women applauding, I'll clear the court.
"""

CONTENT_INQUISITION = """Linkman: Jarrow - New Year's Eve 1911
Reg:
(Graham) Trouble at mill.
Lady Mountback:
(Carol) Oh no - what kind of trouble?
Reg: I don't know - Mr Wentworth told me to come and say that there was trouble at the mill, that's all - I didn't expect a kind of Spanish Inquisition.
[JARRING CHORD]
(The door flies open and Cardinal Ximinez of Spain enters, flanked by two junior cardinals. Cardinal Biggles has goggles pushed over his forehead. Cardinal Fang is just Cardinal Fang)
Ximinez:
(Michael) NOBODY expects the Spanish Inquisition! Our weapon is suprise...surprise and fear...fear and surprise.... Our two weapons are fear and surprise...and ruthless efficiency.... Our three weapons are fear, and surprise, and the ruthless efficiency...and an almost fanatical devotion to the Pope.... Amongst our weapons...are fear, surprise, ruth... Amongst our weaponry...are such elements as fear... I'll come in again.
(Exit and exeunt)
Reg: I didn't expect a kind of Spanish Inquisition.
[JARRING CHORD]
(The cardinals burst in)
Ximinez: NOOOBODY expects the Spanish Inquisition! Amongst our weaponry are such diverse elements as: fear, surprise, ruthless efficiency, and an almost fanatical devotion to the Pope, and a night out with the neighbour - Oh erh! It's no good, I'm sorry. Cardinal Biggles - you'll have to say it.
Biggles:
(Terry J) What?
Ximinez: You'll have to say the bit about 'Our chief weapons are ...'
Biggles: I couldn't say that...
(Ximinez bundles the cardinals outside again)
Reg: I didn't expect a kind of Spanish Inquisition.
[JARRING CHORD]
(The cardinals enter)
Biggles: Er.... Nobody...um....
Ximinez: Expects...
Biggles: Expects... Nobody expects the...um...Spanish...um...
Ximinez: Inquisition.
Biggles: Nobody expects the Spanish Inquisition. In fact, those who do expect -
Ximinez: Our chief weapons is...
Biggles: Our chief weapons is...um...er...
Ximinez: Surprise...
Biggles: Surprise and --
Ximinez: Stop. Stop. Stop there - All right! All right! ...our chief weapon is surprise...blah blah blah blah blah. Now, Cardinal Fang, read the charges.
Fang:
(Terry G) One pound for a full sketch, 24 p for a quickie.
Ximinez: What will you have?
Lady Mountback: Sketch, please. 
"""

HERE = os.path.dirname(os.path.abspath(__file__))

class Test(unittest.TestCase):
    """Tests for FileField"""

    def setUp(self):
        class Skit(ep.Object):
            title = ep.f.CharacterVarying(length=16)
            content = ep.f.FileField()

        class Jpeg(ep.Object):
            title = ep.f.CharacterVarying(length=16)
            content = ep.f.FileField(mimetype='image/jpeg')

        self.Skit = Skit
        self.Jpeg = Jpeg
        self.conn = get_test_conn()
        ep.set_context(self.conn)
        ep.start_session()
        parrot = Skit(title='parrot')
        ep.add(parrot)
        parrot.content.filename='parrot.txt'
        parrot.content.write(CONTENT_PARROT)
        hungarian = Skit(title='hungarian')
        ep.add(hungarian)
        hungarian.content.filename='hungarian.txt'
        hungarian.content.mimetype='text/x-rst'
        hungarian.content.write(CONTENT_HUNGARIAN)
        img = Jpeg(title='pythons')
        ep.add(img)
        img.content.import_(os.path.join(HERE, 'pythons.yotpeg'))
        inquisition = Skit(title='inquisition')
        ep.add(inquisition)
        inquisition.content.filename='inquisition'
        inquisition.content.write(CONTENT_INQUISITION)
        ep.commit()

    def tearDown(self):
        self.conn.rollback()
        try:
            self.conn.cursor().execute('DROP TABLE skits;')
            self.conn.cursor().execute('DROP TABLE jpegs;')
            self.conn.commit()
        except ProgrammingError:
            pass

    def test_read(self):
        """Simple test for reading a lobject content"""
        ep.start_session()
        parrot = self.Skit.get(1)
        content = parrot.content.read()
        self.assertEqual(content, CONTENT_PARROT)

    def test_delete(self):
        """Check if no garbage is left after we delete object containg lobject
        """
        ep.start_session()
        parrot = self.Skit.get(1)
        oid = parrot.content.oid
        parrot.delete()
        ep.commit()
        self.assertRaises(OperationalError, lambda: self.conn.lobject(oid))

    def test_unlink(self):
        """Check if unlinking an lobject is handled by None'ing a field"""
        ep.start_session()
        parrot = self.Skit.get(1)
        parrot.content.unlink()
        ep.commit()
        ep.start_session()
        parrot = self.Skit.get(1)
        self.assertEqual(parrot.content.read(), '')

    def test_size(self):
        """Test getting the size. As it involves seek()ing also check if
        position is unchanged"""
        ep.start_session()
        parrot = self.Skit.get(1)
        parrot.content.seek(10)
        self.assertEqual(parrot.content.get_size(), len(CONTENT_PARROT))
        self.assertEqual(parrot.content.tell(), 10)

    def test_mime(self):
        """Test if you can get a guessed mimetype"""
        ep.start_session()
        parrot = self.Skit.get(1)
        self.assertEqual(parrot.content.filename, 'parrot.txt')
        self.assertEqual(parrot.content.mimetype, 'text/plain')

    def test_forced_mime(self):
        """Test if you can force the mime to be other than guessed one"""
        ep.start_session()
        hungarian = self.Skit.get(2)
        self.assertEqual(hungarian.content.filename, 'hungarian.txt')
        self.assertEqual(hungarian.content.mimetype, 'text/x-rst')

    def test_fixed_mime(self):
        """Test if you can fix a mime for a field"""
        ep.start_session()
        pythons = self.Jpeg.get(1)
        self.assertEqual(pythons.content.filename, 'pythons.yotpeg')
        self.assertEqual(pythons.content.mimetype, 'image/jpeg')
        def broken():
            pythons.content.mimetype = 'image/png'
        self.assertRaises(AttributeError, broken)

    def test_import(self):
        """Test if you can import a file content from the filesystem"""
        ep.start_session()
        pythons = self.Jpeg.get(1)
        self.assertEqual(pythons.content.get_size(), os.path.getsize(
            os.path.join(HERE, 'pythons.yotpeg')
        ))

        
    def test_no_mime(self):
        """Test if without a mimetype we get application/octet-stream"""
        ep.start_session()
        inquisition = self.Skit.get(3)
        self.assertEqual(
            inquisition.content.mimetype, 'application/octet-stream'
        )

    def test_assigment(self):
        """Ensure we can't use assignment to set the file field value"""
        ep.start_session()
        inquisition = self.Skit.get(3)
        def broken():
            inquisition.content = 'xxx'
        self.assertRaises(AttributeError, broken)

    def test_not_added(self):
        """Ensure trying to write to a file without a session raises exc"""
        ep.start_session()
        parrot2 = self.Skit(title='parrot2')
        def broken():
            parrot2.content.write(CONTENT_PARROT)
        self.assertRaises(ep.object.exc.LifecycleError, broken)

    @unittest.skipIf(webtest is None, 'No WebTest, skipping serve() test')
    def test_serve(self):
        """Test the WSGI feature of the file field."""
        ep.start_session()
        pythons = self.Jpeg.get(1)
        app = webtest.TestApp(pythons.content.serve())
        res = app.get('/')
        with open(os.path.join(HERE, 'pythons.yotpeg'), 'rb') as f:
            self.assertEqual(res.body, f.read())
            self.assertEqual(
                res.headers['Content-Disposition'], 
                'attachment; filename="pythons.yotpeg"'
            )
            self.assertEqual(res.headers['Content-Type'], 'image/jpeg')
