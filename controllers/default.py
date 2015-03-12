# -*- coding: utf-8 -*-
### required - do no delete

from datetime import datetime

def user(): return dict(form=auth())
def download(): return response.download(request,db)

def call():
    session.forget()
    return service()

# this is the Ajax callback
@auth.requires_login()
def follow():
   if request.env.request_method!='POST': raise HTTP(400)
   if request.args(0) =='follow' and not db.followers(follower=me,followee=request.args(1)):
       # insert a new friendship request
       db.followers.insert(follower=me,followee=request.args(1))
   elif request.args(0)=='unfollow':
       # delete a previous friendship request
       db(db.followers.follower==me)(db.followers.followee==request.args(1)).delete()



### end requires

def index():
  #  me_and_my_followees = [me]+[row.followee for row in my_followees.select(db.followers.followee)]
    followers = db(db.followers.follower==me).select()
   
    return locals()
    # return dict(my_followees=my_followees, me_and_my_followees=me_and_my_followees)

# a page for searching for other users
@auth.requires_login()
def search():
   form = SQLFORM.factory(Field('name',requires=IS_NOT_EMPTY()))
   if form.accepts(request):
       tokens = form.vars.name.split()
       query = reduce(lambda a,b:a&b,
                      [db.auth_user.first_name.contains(k)|db.auth_user.last_name.contains(k) \
                           for k in tokens])
       people = db(query).select(orderby=db.auth_user.first_name|db.auth_user.last_name,left=db.followers.on(db.followers.followee==db.auth_user.id))
   else:
       people = []
   return locals()

def error():
    return dict()

@auth.requires_login()
def mycal():
    rows=db(db.t_appointment.created_by==auth.user.id).select()
    return dict(rows=rows)

@auth.requires_login()
def appointment_create():
#    select_imagefiles=db(db.images_table.uploader==auth.user.id).select()
    form=crud.create(db.t_appointment,
                     onvalidation=geocode2,
                     next='appointment_read/[id]')
    #newform = crud.create(db.images_table, onvalidation=geocode2, next='appointment_read/[id]')
    #return dict(form=form, newform=newform)
    return dict(form=form)

@auth.requires_login()
def appointment_read():
    record = db.t_appointment(request.args(0)) or redirect(URL('error'))
    form=crud.read(db.t_appointment,record)
    return locals()

#@auth.requires_signature()
@auth.requires_login()
def appointment_update():
      # if auth.user_id == row.user_id:
      record = db.t_appointment(request.args(0)) or redirect(URL('error'))
      form=crud.update(db.t_appointment,record,next='appointment_read/[id]',
                     onvalidation=geocode2,
                     ondelete=lambda form: redirect(URL('appointment_select')),
                     onaccept=crud.archive)
      return dict(form=form)

@auth.requires_login()
# people = db(query).select(orderby=db.auth_user.first_name|db.auth_user.last_name,left=db.followers.on(db.followers.followee==db.auth_user.id))
def appointment_select():

   my_followees = db(db.followers.follower==me)

   me_and_my_followees = [me]+[row.followee for row in my_followees.select(db.followers.followee)]
   #Pull all weets to be displayed
   #  appts = db(db.weets.posted_by.belongs(me_and_my_followees)).select(orderby=~db.weets.posted_on,limitby=(0,100))
   #  return locals()


   present = datetime.now()
   q = db.t_appointment.f_end_time > present
   f,v=request.args(0),request.args(1)
   query=f and db.t_appointment[f]==v or db.t_appointment
   rows=db(q)(db.t_appointment.created_by.belongs(me_and_my_followees)).select(orderby=db.t_appointment.f_start_time, limitby=(0,100))
   return dict(rows=rows)



@auth.requires_login()
def appointment_search():
    form, rows=crud.search(db.t_appointment)
    return dict(form=form, rows=rows)

def ifollow():
    query =''
    my_followees = db(db.followers.follower==me)
    followlist = db().select(db.followers.ALL)
    people = db(query).select(left=db.followers.on(db.followers.follower==db.auth_user.id), distinct=True)

    return locals()
