from .models import assignments as _assignments
from .models import courses as _courses
from .models import course_rosters as _course_rosters
from .models import submissions as _submissions
from .models import files as _files
from .models import comments as _comments
from .models import sections as _sections
from .models import rubric_categories as _rubric_categories
from .models import rubric_comments as _rubric_comments

assignment = _assignments.Assignments()
course = _courses.Courses()
roster = _course_rosters.CourseRosters()
submission = _submissions.Submissions()
file = _files.Files()
comment = _comments.Comments()
section = _sections.Sections()
rubric_category = _rubric_categories.RubricCategories()
rubric_comment = _rubric_comments.RubricComments()
