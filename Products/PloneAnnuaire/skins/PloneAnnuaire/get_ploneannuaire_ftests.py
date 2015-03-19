## Script (Python) "get_plonearticle_ftests"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
selenium = context.portal_selenium
suite = selenium.getSuite()
target_language = 'en'
suite.setTargetLanguage(target_language)

selenium.addUser(id='sampleadmin', fullname='Sample Admin',
                 roles=['Member', 'Manager'])
selenium.addUser(id='samplemember', fullname='Sample Member',
                 roles=['Member'])

# 1
test_logout = suite.TestLogout()
test_admin_login = suite.TestLoginPortlet('sampleadmin')
test_member_login = suite.TestLoginPortlet('samplemember')
test_switch_language = suite.TestSwitchToLanguage()


annuaire_fields = []
annuaire_fields.append({'id': 'title',
                        'value': 'Test Annuaire'})
annuaire_fields.append({'id': 'description',
                        'value': 'This is the test annuaire'})
annuaire = {'type': 'PloneAnnuaire',
            'id': 'testannuaire',
            'fields': annuaire_fields}

annuaire_contact_fields = []
annuaire_contact_fields.append(
    {'id': 'title',
      'value': 'Test Annuaire Contact'})
annuaire_contact_fields.append(
    {'id': 'variants',
      'value': 'The test annuaire contact variants'})
annuaire_contact_fields.append(
    {'id': 'contact',
      'value': 'The test annuaire contact text'})
annuaire_contact = {
    'type': 'PloneAnnuaireContact',
    'id': 'testannuairecontact',
    'fields': annuaire_contact_fields,
    }


def test_add_annuaire(folder, info):
    return suite.test_add_content(folder, info)


def test_add_annuaire_contact(folder, info):
    return suite.test_add_content(folder, info)

suite.addTests("PloneAnnuaire",
          'Login as Sample Member',
          test_logout,
          test_member_login,
          test_switch_language,
          'Add Annuaire',
          test_add_annuaire('/Members/samplemember', annuaire),
          'Add Annuaire Contact',
          test_add_annuaire_contact(
              '/Members/samplemember/%s' % annuaire['id'],
              annuaire_contact),
         )

return suite
