----------------------------------------
First steps with Elephantoplasty
----------------------------------------

Let's start our tutorial creating an empty PostgresSQL database. Let's assume
it's on the local machine, it's called "eptest" and it's owned by user 
"eptester" with password "secret". No let's play a little with it:

.. testcode::

    import eplasty as ep

    ep.connect(
        host='localhost', database='eptest', user='eptester', password='secret'
    )

    # Then we create some records
    ep.start_session()
    
    class Knight(ep.Object):
        title = ep.f.CharacterVarying(length=5, null=False, default='Sir')
        name = ep.f.CharacterVarying(length=20, null=False)
        nickname = ep.f.CharacterVarying(length=20, null=True)

        def __str__(self):
            parts = [self.title, self.name]
            if self.nickname:
                parts.append(self.nickname)
            return ' '.join(parts)

    galahad = Knight(name='Galahad', nickname='The Pure')
    arthur = Knight(title='King', name='Arthur')
    lancelot = Knight(name='Lancelot')
    ep.add(galahad, arthur, lancelot)
    ep.commit()
    
    # And then we retrieve them
    ep.start_session()
    knights = Knight.find()
    for k in knights:
        print k
        k.delete()
    ep.commit()

The above will produce this:

.. testoutput::

    Sir Galahad The Pure
    King Arthur
    Sir Lancelot
