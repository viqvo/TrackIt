# -*- coding: utf-8 -*-
# try something like
import json
import re

@auth.requires_login()
def edit():
    """Allows editing of a friend list."""

    # Prepares an add form.
    form = SQLFORM.factory(
        Field('friends', 'text', default='No friends yet', writable=False),
        Field('add_friends', 'text'),
        submit_button = T('Add'),
        _id="email-form"
        )
    
    # A few URLs.
    get_friend_url = URL('get_friends', user_signature=True)
    add_friend_url = URL('add_friends', user_signature=True)
    del_friend_url = URL('del_friend', user_signature=True)
    back_url = URL('default', 'index')

    return dict(form=form,
                get_friend_url=get_friend_url,
                add_friend_url=add_friend_url,
                del_friend_url=del_friend_url,
                back_url=back_url,
                )


@auth.requires_login()
@auth.requires_signature()
def get_friends():
    """Get friend list."""
    friend_rows = db(db.friend.user_id == auth.user_id).select()
    friend_list = [r.friend for r in friend_rows]
    logger.info("We are sending the friend list: %r" % friend_list)
    return response.json(dict(friends=friend_list))

    
email_split_pattern = re.compile('[,\s]+')
whitespace = re.compile('\s+$')

def split_emails(s):
    """Splits the emails that occur in a string s, returning the list of emails."""
    l = email_split_pattern.split(s)
    if l == None:
        return []
    else:
        r = []
        for el in l:
            if len(el) > 0 and not whitespace.match(el):
                r += [el.lower()]
        return r

def normalize_email_list(l):
    if isinstance(l, basestring):
        l = [l]
    r = []
    for el in l:
        ll = split_emails(el)
        for addr in ll:
            if addr not in r:
                r.append(addr.lower())
    r.sort()
    return r

class EMAILS(object):
    def __call__(self, value):
        bad_emails = []
        emails = []
        f = IS_EMAIL()   
        for email in split_emails(value):
            emails.append(email)
            error = f(email)[1]
            if error: bad_emails.append(email)
        if not bad_emails:
            return (value, None)
        else:
            return (value, T('Invalid emails: ') + ', '.join(bad_emails))
    def formatter(self, value):
        return ', '.join(value or [])

@auth.requires_login()
@auth.requires_signature()
def add_friends():
    """This is a json function that adds friends.  The arguments is the 
    list_id, and as variable friends, it contains the friends to be added.
    It returns a json dictionary with fields:
     - msg: if "ok" all is ok;
     - friends: the new friend list."""
    friend_rows = db(db.friend.user_id == auth.user_id).select()
    current_friends = [r.friend for r in friend_rows]
    logger.info("Current friends: %r" % current_friends)
    if request.vars.friends is None:
        new_friends = []
    else:
        new_friends = json.loads(request.vars.friends)
        logger.info("New friends: %r" % new_friends)
        if new_friends is None: raise HTTP(403, 'Invalid arguments')
        _, error_msg = EMAILS()(new_friends)
        if error_msg:
            logger.info("Error: %r" % error_msg)
            return response.json(dict(msg=error_msg, friends=None))
    new_friends = normalize_email_list(new_friends)
    if len(new_friends) > 100:
        logger.info("Too many friends added: %d" % len(new_friends))
        return response.json(dict(msg='Please add at most 100 friends at a time.', friends=None))
    new_friends = list(set(new_friends) - set(current_friends))
    logger.info("New friends to insert: %r" % new_friends)
    for f in new_friends:
        db.friend.insert(friend=f)
    current_friends.extend(new_friends)
    current_friends.sort()
    return response.json(dict(msg="ok", friends=current_friends))
    

@auth.requires_login()
@auth.requires_signature()
def del_friend():
    """This is a json function that deletes a friend."""
    friend_rows = db(db.friend.user_id == auth.user_id).select()
    current_friends = [r.friend for r in friend_rows]
    del_friend = json.loads(request.vars.friend)
    logger.info("del_friend: %r" % del_friend)
    if del_friend is None: raise HTTP(403, 'Invalid arguments')
    del_friend = del_friend.lower()
    if del_friend not in current_friends: raise HTTP(403, 'Invalid arguments')
    logger.info("Removing friend: %r" % del_friend)
    current_friends.remove(del_friend)
    # Updates the list.
    db((db.friend.user_id == auth.user_id) & (db.friend.friend == del_friend)).delete()
    return response.json(dict(msg="ok"))
