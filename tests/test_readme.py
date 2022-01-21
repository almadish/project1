
from solution import *

# import markdown parsers
import markdown
from mdx_gfm import GithubFlavoredMarkdownExtension
from bs4 import BeautifulSoup

# start logging
import logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# open the markdown file
readme = open('README.md').read() # extract text from file

class Tests:

    def test_sql_code(self):
        """Test the given contents of the README.md file"""

        # get readme document as github-flavored markdown
        html = markdown.markdown(readme, extensions=[GithubFlavoredMarkdownExtension()]) # get content as object

        # convert to html
        soup = BeautifulSoup(html, 'html.parser')

        # a list of all the code samples
        codes = soup.find_all('code')

        logger.warning(soup)
        assert len(codes) == 32
