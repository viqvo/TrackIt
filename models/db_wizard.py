### we prepend t_ to tablenames and f_ to fieldnames for disambiguity


########################################
db.define_table('t_appointment',
    Field('id','id', readable=False,
          represent=lambda id:SPAN(id,' ',A('view',_href=URL('appointment_read',args=id)))),
    Field('f_title', type='string', notnull=True,
          label=T('Title')),
    Field('f_start_time', type='datetime',
          label=T('Start Time')),
    Field('f_end_time', type='datetime',
          label=T('End Time')),
    Field('f_location', type='string',
          label=T('Location')),
    Field('f_log', type='text',
          label=T('Details')),
    #Field('active','boolean',default=True, readable=False, writable=False),
    Field('created_on','datetime',default=request.now,
          label=T('Created On'),writable=False,readable=False),
    Field('modified_on','datetime',default=request.now,
          label=T('Modified On'),writable=False,readable=False,
          update=request.now),
    Field('created_by',db.auth_user,default=auth.user_id,
          label=T('Created By'),writable=False,readable=False),
    Field('image', 'upload'),
    #Field('modified_by',db.auth_user,default=auth.user_id,
    #      label=T('Modified By'),writable=False,readable=False,
    #      update=auth.user_id),
    format='%(f_title)s',
    migrate=settings.migrate)


db.define_table('t_appointment_archive',db.t_appointment,Field('current_record','reference t_appointment'))

db.define_table('images_table', 
                Field ('imagefile', 'upload'),
                Field('imagetitle'),
                Field('uploader', 'reference auth_user', default=auth.user_id, writable=False)
                )

db.define_table('followers',
   Field('user_id', db.auth_user, default=auth.user_id),
   Field('follower','reference auth_user'), #who follows u
   Field('followee','reference auth_user')) #who you follow
#Convenience methods to make code more compact
me = auth.user_id




def geocode2(form):
    from gluon.tools import geocode
    lo,la= geocode(form.vars.f_location+' USA')
    form.vars.f_latitude=la
    form.vars.f_longitude=lo
