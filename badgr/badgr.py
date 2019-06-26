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
import re 
import functools
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
from courseware.model_data import ScoresClient

logger = logging.getLogger(__name__)
loader = ResourceLoader(__name__)

from xblock.validation import ValidationMessage
from courseware.model_data import ScoresClient
from opaque_keys.edx.keys import UsageKey
from opaque_keys import InvalidKeyError


ISSUER_ID = 'MC67oN42TPm9VARGW7TmKw'


def load(path):
    logger.info("In _actions_generator..")

    """Handy helper for getting resources from our kit."""
    data = pkg_resources.resource_string(__name__, path)
    return data.decode("utf8")


def _actions_generator(block):  # pylint: disable=unused-argument
    logger.info("In _actions_generator..")

    """ Generates a list of possible actions to
    take when the condition is met """

    return [
        {"display_name": "Display a message",
         "value": "display_message"},
        {"display_name": "Redirect using jump_to_id",
         "value": "to_jump"},
        {"display_name": "Redirect to a given unit in the same subsection",
         "value": "to_unit"},
        {"display_name": "Redirect to a given URL",
         "value": "to_url"}
    ]


def _conditions_generator(block):  # pylint: disable=unused-argument
    """ Generates a list of possible conditions to evaluate """
    logger.info("In _conditions_generator..")

    return [
        {"display_name": "Grade of a problem",
         "value": "single_problem"},
        {"display_name": "Average grade of a list of problems",
         "value": "average_problems"}
    ]


def _operators_generator(block):  # pylint: disable=unused-argument
    """ Generates a list of possible operators to use """
    logger.info("In _operators_generator..")

    return [
        {"display_name": "equal to",
         "value": "eq"},
        {"display_name": "not equal to",
         "value": "noeq"},
        {"display_name": "less than or equal to",
         "value": "lte"},
        {"display_name": "less than",
         "value": "lt"},
        {"display_name": "greater than or equal to",
         "value": "gte"},
        {"display_name": "greater than",
         "value": "gt"},
        {"display_name": "none of the problems have been answered",
         "value": "all_null"},
        {"display_name": "all problems have been answered",
         "value": "all_not_null"},
        {"display_name": "some problem has not been answered",
         "value": "has_null"}
    ]


def n_all(iterable):
    """
    This iterator has the same logic of the function all() for an array.
    But it only responds to the existence of None and not False
    """
    logger.info("In n_all..")

    for element in iterable:
        if element is None:
            return False
    return True



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
    logger.info("In no_award_received..")

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
        display_name="Problem ID",
        help="IMPORTANT: Problem id to use for the condition.  (Not the "
                        "complete problem locator. Only the 32 characters "
                        "alfanumeric id. "
                        "Example: 618c5933b8b544e4a4cc103d3e508378)",
        scope=Scope.settings,
        default=u""
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


    # def validate_field_data(self, validation, data):
    #     """
    #     Validate this block's field data
    #     """
    #     logger.info("In validate_field_data..")

    #     if data.tab_to <= 0:
    #         validation.add(ValidationMessage(
    #             ValidationMessage.ERROR,
    #             u"Tab to redirect to must be greater than zero"))
    #     if data.ref_value < 0 or data.ref_value > 100:
    #         validation.add(ValidationMessage(
    #             ValidationMessage.ERROR,
    #             u"Score percentage field must "
    #             u"be an integer number between 0 and 100"))


    def get_location_string(self, locator, is_draft=False):
        """  Returns the location string for one problem, given its id  """
        # pylint: disable=no-member


        if type(locator) == type([]):
            locator = locator[0]
        if len(locator) == 0:
            return ""
        logger.info("In get_location_string..")
    
        course_prefix = 'course'
        resource = 'problem'
        course_url = unicode(self.course_id)
        if is_draft:
            course_url = course_url.split(self.course_id.run)[0]
            prefix = 'i4x://'
            location_string = '{prefix}{couse_str}{type_id}/{locator}'.format(
                prefix=prefix,
                couse_str=course_url,
                type_id=resource,
                locator=locator)
        else:
            course_url = course_url.replace(course_prefix, '', 1)
            location_string = '{prefix}{couse_str}+{type}@{type_id}+{prefix}@{locator}'.format(
                prefix=self.course_id.BLOCK_PREFIX,
                couse_str=course_url,
                type=self.course_id.BLOCK_TYPE_PREFIX,
                type_id=resource,
                locator=locator)
        logger.info("In get_location_string.. the location string is: {}".format(location_string))

        return location_string


    def get_condition_status(self):
        """  Returns the current condition status  """
        logger.info("In get_condition_status..")

        condition_reached = True
        problems = []
        num_problems = 0
        # hack to initialize condition and operator variables
        self.list_of_problems
        self.operator = "gte" 
        if self.problem_id and self.condition == 'single_problem':
            
            # now split problem id by spaces or commas
            problems = re.split('\s*,*|\s*,\s*', self.problem_id)
            num_problems = len(problems)
            problems = filter(None, problems)

            problems = problems[:1]
            logger.info("NUMBER 1 .. problems: {}".format(problems))

        elif self.list_of_problems and self.condition == 'average_problems':
            logger.info("NUMBER 2.. self.list_of_problems is: {}".format(self.list_of_problems))
            # now split list of problems id by spaces or commas
            problems = [re.split('\s*,*|\s*,\s*', x) for x in self.list_of_problems]

            num_problems = len(problems)
            np = []
            # [np.append(p) for p in problems if p != "" and p != u'' and p != [u'']]
            for p in problems:
                if p != '' and p != u'' and p != [u'']:
                    logger.info("In get_condition_status.. keeping: {}".format(p))
                    np.append(p)
            problems = np

            logger.info("In get_condition_status.. the problems are: {}".format(problems))
            problems = filter(None, problems)
            logger.info("NUMBER 2.. problems: {}".format(problems))


        else:
            logger.info("In get_condition_status.. I SHOULD NOT BE HERE... SHOULD I?")
            condition_reached = None
        if type(problems[0]) == type([]):
            problems = problems[0]

        ret = []
        for p in problems:
            if p != "" and p != u'' and p != [u'']:
                logger.info("In get_condition_status.. keeping: {}".format(p))
                ret.append(p)
            else:
                logger.info("In get_condition_status.. discarding from problems list: {}".format(p))

        problems = ret

        if problems:
            logger.info("In get_condition_status.. problems (final): {}".format(problems))
            condition_reached = self.condition_on_problem_list(problems)


        logger.info("INFO In get_condition_status.. self.condition is: {} and len(problems) is {} and num_problems is: {}"
                .format(self.condition, len(problems), num_problems))
        if len(problems) < num_problems:
            condition_reached = None 

        logger.info("In get_condition_status.. the condition_reached is: {}".format(condition_reached))
        return condition_reached

    def compare_scores(self, correct, total):
        """  Returns the result of comparison using custom operator """

        result = False
        if total:
            # getting percentage score for that section
            percentage = (correct / total) * 100

            if self.operator == 'eq':
                result = percentage == self.pass_mark
            if self.operator == 'noeq':
                result = percentage != self.pass_mark
            if self.operator == 'lte':
                result = percentage <= self.pass_mark
            if self.operator == 'gte':
                result = percentage >= self.pass_mark
            if self.operator == 'lt':
                result = percentage < self.pass_mark
            if self.operator == 'gt':
                result = percentage > self.pass_mark
        logger.info("In compare_scores.. the result is: {} the percentage is: {}".format(result, percentage))
        return result

    def are_all_not_null(self, problems_to_answer):
        """  Returns true when all problems have been answered """
        logger.info("In are_all_not_null..")

        result = False
        all_problems_were_answered = n_all(problems_to_answer)
        if problems_to_answer and all_problems_were_answered:
            result = True
        return result

    def has_null(self, problems_to_answer):
        """  Returns true when at least one problem have not been answered """
        logger.info("In has_null..")

        result = False
        all_problems_were_answered = n_all(problems_to_answer)
        if not problems_to_answer or not all_problems_were_answered:
            result = True
        return result

    def are_all_null(self, problems_to_answer):
        """  Returns true when all problems have not been answered """
        logger.info("In are_all_null..")

        for element in problems_to_answer:
            if element is not None:
                return False
        return True


    SPECIAL_COMPARISON_DISPATCHER = {
        'all_not_null': are_all_not_null,
        'all_null': are_all_null,
        'has_null': has_null
    }


    @property
    def problem_id(self):
        logger.info("In problem_id..")
        return self.section_title


    @property
    def list_of_problems(self): 

        logger.info("In list_of_problems..")
        problems = re.split('\s*,*|\s*,\s*', self.problem_id)
        filter(None, problems)
        num_problems = len(problems)
        if num_problems == 0:
            pass
        elif num_problems == 1:
            self.condition = 'single_problem'
        else:
            self.condition = 'average_problems'
        return problems


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
        logger.info("In api_url..")
        return self.get_xblock_settings().get('BADGR_BASE_URL' '')


    @property
    def current_user_key(self):
        logger.info("In current_user_key..")
        user = self.runtime.service(self, 'user').get_current_user()
        # We may be in the SDK, in which case the username may not really be available.
        return user.opt_attrs.get('edx-platform.username', 'username')


    @XBlock.json_handler
    def no_award_received(self, data, suffix=''):
        """
        The json handler which uses the badge service to deal with no
        badge being earned.
        """
        logger.info("In no_award_received..")
        self.received_award = False
        self.check_earned = True

        return {"image_url": self.image_url, "assertion_url": self.assertion_url}

  
    @XBlock.json_handler
    def new_award_badge(self, data, suffix=''):
        """
        The json handler which uses the badge service to award
        a badge.
        """
        logger.info("In new_award_badge..")


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
    def condition_status_handler(self, data, suffix=''):  # pylint: disable=unused-argument
        """  Returns the actual condition state  """


        condition_status = self.get_condition_status()
        abort = None 
        if condition_status == None:
            abort = True

        logger.info("INFO In condition_status_handler.. the condition_status returned is: {} abort is: {}".format(condition_status, abort))
        return {'status': condition_status, 'abort': abort }


    def get_course_problems_usage_key_list(self):
        logger.info("In get_course_problems_usage_key_list..")
        return StudentModule.objects.filter(course_id__exact=self.course_id, grade__isnull=False,module_type__exact="problem").values('module_state_key')

        
    def get_this_parents_children(self):
        logger.info("In get_this_parents_children..")
        return self.get_parent().get_children()
        # return {"parent_name": parent.name, "children": "children.list"}


    def condition_on_problem_list(self, problems):
        logger.info("In condition_on_problem_list.. (input) problems: {}".format(problems))
        """ Returns the score for a list of problems """
        # pylint: disable=no-member
        user_id = self.xmodule_runtime.user_id
        scores_client = ScoresClient(self.course_id, user_id)
        correct_neutral = {'correct': 0.0}
        total_neutral = {'total': 0.0}
        total = 0
        correct = 0

        def _get_usage_key(problem):
            loc = self.get_location_string(problem)
            try:
                uk = UsageKey.from_string(loc)
            except InvalidKeyError:
                uk = _get_draft_usage_key(problem)
            return uk

        def _get_draft_usage_key(problem):
            loc = self.get_location_string(problem, True)
            try:
                uk = UsageKey.from_string(loc)
                uk = uk.map_into_course(self.course_id)
            except InvalidKeyError:
                uk = None
            return uk

        def _to_reducible(score):
            correct_default = 0.0
            total_default = 1.0
            if not score.total:
                return {'correct': correct_default, 'total': total_default}
            else:
                return {'correct': score.correct, 'total': score.total}
        def _calculate_correct(first_score, second_score):
            correct = first_score['correct'] + second_score['correct']
            return {'correct': correct}

        def _calculate_total(first_score, second_score):
            total = first_score['total'] + second_score['total']
            return {'total': total}

        usages_keys = map(_get_usage_key, problems)
        scores_client.fetch_scores(usages_keys)
        scores = map(scores_client.get, usages_keys)
        scores = filter(None, scores)
        problems_to_answer = [score.total for score in scores]

        if self.operator in self.SPECIAL_COMPARISON_DISPATCHER.keys():
            evaluation = self.SPECIAL_COMPARISON_DISPATCHER[self.operator](self, problems_to_answer)
            logger.info("WTF: In condition_on_problem_list.. the evaluation is: {}".format(evaluation))

            return evaluation
        reducible_scores = map(_to_reducible, scores)
        correct = reduce(_calculate_correct, reducible_scores, correct_neutral)
        total = reduce(_calculate_total, reducible_scores, total_neutral)
        logger.info("HERE: In condition_on_problem_list.. the total is: {} the correct is: {}".format(total['total'], correct['correct']))
        return self.compare_scores(correct['correct'], total['total'])


    # def get_location_string(self, locator, is_draft=False):
    #     """  Returns the location string for one problem, given its id  """
    #     # pylint: disable=no-member
    #     course_prefix = 'course'
    #     resource = 'problem'
    #     course_url = self.course_id.to_deprecated_string()
    #     if is_draft:
    #         course_url = course_url.split(self.course_id.run)[0]
    #         prefix = 'i4x://'
    #         location_string = '{prefix}{couse_str}{type_id}/{locator}'.format(
    #             prefix=prefix,
    #             couse_str=course_url,
    #             type_id=resource,
    #             locator=locator)
    #     else:
    #         course_url = course_url.replace(course_prefix, '', 1)
    #         location_string = '{prefix}{couse_str}+{type}@{type_id}+{prefix}@{locator}'.format(
    #             prefix=self.course_id.BLOCK_PREFIX,
    #             couse_str=course_url,
    #             type=self.course_id.BLOCK_TYPE_PREFIX,
    #             type_id=resource,
    #             locator=locator)

    #     return location_string


    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        logger.info("In resource_string..")
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")


    @XBlock.supports("multi_device")
    def student_view(self, context=None):
        """
        The primary view of the BadgrXBlock, shown to students
        when viewing courses.
        """
        logger.info("In student_view..")
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
        logger.info("In studio_view..")
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
        logger.info("In workbench_scenarios..")
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






























































































