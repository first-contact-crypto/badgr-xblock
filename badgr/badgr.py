"""TO-DO: Write a description of what this XBlock is.
Just to trigger a change.. remove me !!
"""
# Examples:
# * Old style: "i4x://edX/DemoX.1/problem/466f474fa4d045a8b7bde1b911e095ca"
# * New style: "block-v1:edX+DemoX.1+2014+type@problem+block@466f474fa4d045a8b7bde1b911e095ca"

# Old style usage IDs are missing course run information (note the missing
# "2004" in the example above). We call map_into_course() to add that
# potentially missing information. That way, we can later get a complete
# CourseKey via usage_key.course_key

# Note: Keys are immutable -- map_into_course() is returning a new key,
#       not modifying the old one.
# try:
#     # Returns a subclass of UsageKey, depending on what's being parsed.
#     usage_key = UsageKey.from_string(usage_id).map_into_course(course_key)
# except InvalidKeyError:
#     # We don't recognize this key

# To serialize back into strings, just call unicode() on them or pass
# them to format() like you'd expect.
# print "Course: {}".format(course_key)
# print "Usage: {}".format(usage_key)

import os
import json
import pkg_resources
import logging
import requests
from django.conf import settings
from xblock.core import XBlock
from django.core.files import File
from django.core.files.images import ImageFile
from django.contrib.auth.models import User
from xblock.fields import Scope, Integer, String, Float, List, Boolean, ScopeIds
from xblockutils.resources import ResourceLoader
from xblock.fragment import Fragment
from xblockutils.studio_editable import StudioEditableXBlockMixin
from xblockutils.settings import XBlockWithSettingsMixin

# from submissions.models import score_set
# from django.dispatch import receiver
from courseware.models import StudentModule

logger = logging.getLogger(__name__)
loader = ResourceLoader(__name__)

ISSUER_ID = 'MC67oN42TPm9VARGW7TmKw'



@XBlock.needs('settings')
@XBlock.wants('badging')
@XBlock.wants('user')
class BadgrXBlock(StudioEditableXBlockMixin, XBlockWithSettingsMixin, XBlock):
    """
    TO-DO: document what your XBlock does.
    """

    # Fields are defined on the class.  You can access them in your code as
    # self.<fieldname>.

    # TO-DO: delete count, and define your own fields.
    display_name = String(
        display_name="Display Name",
        help="This name appears in the horizontal navigation at the top of the page.",
        scope=Scope.settings,
        default=u"Step 3. Earn an Epiphany point for the correct answer"
    )

    issuer_slug = String(
        display_name="Issuer name",
        help="DO NOT CHANGE",
        scope=Scope.settings,
        default=u"fcc"
    )

    badge_slug = String(
        display_name="Badge name",
        help="must be lower-case.. and ONLY 'epiphany' or 'course'.",
        scope=Scope.settings,
        default=u"epiphany"
    )

    badge_name = String(
        display_name="Badge display name",
        help="Badge name that appears in Accomplishments tab.. either 'Epiphany' or 'Course'",
        scope=Scope.settings,
        default=u"Epiphany"
    )

    image_url = String(
        help="DO NOT CHANGE",
        scope=Scope.user_state,
        default="https://media.us.badgr.io/uploads/badges/issuer_badgeclass_71b6cc36-d931-446e-909b-ec6465a5cbec.svg"
    )

    criteria = String(
        display_name="Criteria",
        help="How does one earn this badge?",
        scope=Scope.settings,
        default=u"Achieve a pass mark of 70% percent or more"
    )

    description = String(
        display_name="Description",
        help="What is this badge",
        scope=Scope.settings,
        default=u"An Epiphany Point, redeem for prizes."
    )

    section_title = String(
        display_name="Section title",
        help="DO NOT CHANGE",
        scope=Scope.settings,
        default=u"Section"
    )

    pass_mark = Float(
        display_name='Pass mark',
        default=70.0,
        scope=Scope.settings,
        help="Minium grade required to award this badge",
    )

    received_award = Boolean(
        default=False,
        scope=Scope.user_state,
        help='Has the user received a badge for this sub-section'
    )

    check_earned = Boolean(
        default=False,
        scope=Scope.user_state,
        help='Has the user check if they are eligible for a badge.'
    )

    assertion_url = String(
        default=None,
        scope=Scope.user_state,
        help='The user'
    )

    award_message = String(
        display_name='Award message',
        default=u'Well done, Cryptonaut! Proceed to the next mission.',
        scope=Scope.settings,
        help='Message the user will see upon receiving a badge',
    )

    motivation_message = String(
        display_name='Motivational message',
        default=u"Don't worry, try again.",
        scope=Scope.settings,
        help='Message the user will see if they do not quailify for a badge'
    )

    button_text = String(
        display_name='Button text',
        default=u"Click here to claim your reward.",
        scope=Scope.settings,
        help='Text appearing on button'
    )

    button_colour = String(
        display_name='Button colour',
        default=u"#0075b4",
        scope=Scope.settings,
        help='Colour appearing on button'
    )

    button_text_colour = String(
        display_name='Text button colour',
        default=u"#ffffff",
        scope=Scope.settings,
        help='Text colour appearing on button'
    )

    # api_token = String(
    #     display_name='API token',
    #     default=u"",
    #     scope=Scope.settings,
    #     help="blah"
    # )


    editable_fields = (
        'display_name',
        'description',
        'criteria',
        'issuer_slug',
        'badge_slug',
        'badge_name',
        'pass_mark',
        'section_title',
        'award_message',
        'motivation_message',
        'button_text',
        'button_colour',
        'button_text_colour'
    )


    show_in_read_only_mode = True
    # apitoken = None


    # @property
    # def api_token(self):
    #     # if self.apitoken:
    #     #     return self.apitoken
    #     # fpath = '/openedx/data/uploads/badgr/badgr.json'
    #     # f = Path(fpath)
    #     # if not f.is_file():
    #     #     logger.warning("BADGR_XBLOCK: In api_token.. The fpath: {}, DOES NOT EXIT!".format(fpath))
    #     # at = None
    #     # with open(fpath, 'r') as f:
    #     #     info = json.load(f)
    #     #     at = info['badgr_access_token']
    #     return '7glaAeNOPG2PgxTtHpihGpSCJSj1Df'

    def get_course_problems_usage_key_list(self):
        return StudentModule.objects.filter(course_id__exact=self.course_id, grade__isnull=False,module_type__exact="problem").values('module_state_key')

        
    def get_this_parents_children(self):
        return self.get_parent().get_children()
        # return {"parent_name": parent.name, "children": "children.list"}

    # @XBlock.json_handler
    # def test_print_children(self, data, suffix=''):
    #     for child in self.get_this_parents_children():
    #         logger.info("INFO In test_print_children.. a child of this parent is: name={}".format(child.name, ))


    @property
    def api_url(self):
        """
        Returns the URL of the Badgr Server from the Settings Service.
        The URL hould be set in both lms/cms env.json files inside XBLOCK_SETTINGS.
        Example:
            "XBLOCK_SETTINGS": {
                "BadgrXBlock": {
                    "BADGR_BASE_URL": "YOUR URL  GOES HERE"
                }
            },
        """
        return self.get_xblock_settings().get('BADGR_BASE_URL' '')

    # def get_list_of_issuers(self):
    #     """
    #     Get a list of issuers from badgr.proversity.org
    #     """
    #     issuer_list = requests.get('{}/v2/issuers'.format(self.api_url),
    #                                headers={'Authorization': 'Bearer {}'.format(self.api_token)})
    #     return issuer_list.json()

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    # TO-DO: change this view to display your data your own way.
    @XBlock.json_handler
    def new_award_badge(self, data, suffix=''):
        """
        The json handler which uses the badge service to award
        a badge.
        """
        logger.info("In new_award_badge.. the data is {}".format(data))


        e_image = "https://media.us.badgr.io/uploads/badges/issuer_badgeclass_efc20af1-7d43-4d1e-877e-447244ea3fd3.png"
        c_image = "https://media.us.badgr.io/uploads/badges/issuer_badgeclass_63237c1a-3f3d-40b7-9e48-085658d2799f.png"

        bslug_course = "RBNmTgTUTQC4o_0-yDIA4g"
        bslug_epiph = "CM-sak0wQuCty2BfSEle3A"
        bslug = ""

        if self.badge_slug == 'course':
            self.image_url = c_image
            bslug = bslug_course
        else:
            self.image_url = e_image
            bslug = bslug_epiph

        badge_service = self.runtime.service(self, 'badging')

        badge_class = badge_service.get_badge_class(
            slug=self.badge_slug,
            issuing_component=self.issuer_slug,
            display_name = self.display_name,
            description = self.description,
            criteria = self.criteria,
            course_id = self.course_id
        )
        badge_class.badgr_server_slug = bslug
        # badge_class.image_url = self.image_url
        badge_class.save()
        user = User.objects.get(username=self.current_user_key)

        badge_class.award(user)

        self.received_award = True
        self.check_earned = True
        self.assertion_url = "https://firstcontactactcrypto.com/assertions/epiphany.html"

        badge_html_dict = {
            "image_url": self.image_url,
            "assertion_url": self.assertion_url,
            "description": self.description,
            "criteria": self.criteria
        }

        logger.info("BADGR_XBLOCK: In new_award_badge.. this is the html being returned: {}".format(badge_html_dict))

        return badge_html_dict

    @XBlock.json_handler
    def no_award_received(self, data, suffix=''):
        """
        The json handler which uses the badge service to deal with no
        badge being earned.
        """
        self.received_award = False
        self.check_earned = True

        return {"image_url": self.image_url, "assertion_url": self.assertion_url}


    @property
    def current_user_key(self):
        user = self.runtime.service(self, 'user').get_current_user()
        # We may be in the SDK, in which case the username may not really be available.
        return user.opt_attrs.get('edx-platform.username', 'username')



    @XBlock.supports("multi_device")
    def student_view(self, context=None):
        """
        The primary view of the BadgrXBlock, shown to students
        when viewing courses.
        """
        if self.runtime.get_real_user is not None:
            user = self.runtime.get_real_user(
                self.runtime.anonymous_student_id)
        else:
            user = User.objects.get(username=self.current_user_key)

        context = {
            'received_award': self.received_award,
            'check_earned': self.check_earned,
            'section_title': self.section_title,
            'image_url': self.image_url,
            'award_message': self.award_message,
            'button_text': self.button_text,
            'button_colour': self.button_colour,
            'button_text_colour': self.button_text_colour
        }

        frag = Fragment(loader.render_django_template(
            "static/html/badgr.html", context).format(self=self))
        frag.add_css(self.resource_string("static/css/badgr.css"))
        frag.add_javascript(self.resource_string("static/js/src/badgr.js"))
        frag.initialize_js('BadgrXBlock', {
            'user': str(user.username),
            'pass_mark': self.pass_mark,
            'section_title': self.section_title,
            'award_message': self.award_message,
            'motivation_message': self.motivation_message,
            'course_id':  str(self.runtime.course_id),
            'badgrApiToken': "not_needed_??",
            'badge_slug': self.badge_slug
        })

        return frag

    def studio_view(self, context):
        """
        Render a form for editing this XBlock
        """
        frag = Fragment()
        context = {'fields': []}

        # Build a list of all the fields that can be edited:
        for field_name in self.editable_fields:
            field = self.fields[field_name]
            assert field.scope in (Scope.content, Scope.settings), (
                "Only Scope.content or Scope.settings fields can be used with "
                "StudioEditableXBlockMixin. Other scopes are for user-specific data and are "
                "not generally created/configured by content authors in Studio."
            )
            field_info = self._make_field_info(field_name, field)
            if field_info is not None:
                context["fields"].append(field_info)
        frag.content = loader.render_django_template(
            "static/html/badgr_edit.html", context)
        frag.add_javascript(loader.load_unicode("static/js/src/badgr_edit.js"))
        frag.initialize_js('StudioEditableXBlockMixin', {
            'badgrApiToken': "not_needed_??"
        })
        return frag

    # TO-DO: change this to create the scenarios you'd like to see in the
    # workbench while developing your XBlock.
    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("BadgrXBlock",
             """<badgr/>
             """),
            ("Multiple BadgrXBlock",
             """<vertical_demo>
                <badgr/>
                <badgr/>
                <badgr/>
                </vertical_demo>
             """),
        ]






























































































