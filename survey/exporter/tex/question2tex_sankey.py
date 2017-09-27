# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import logging
from builtins import object

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext
from future import standard_library

from survey.models.question import Question

standard_library.install_aliases()


LOGGER = logging.getLogger(__name__)


class Question2TexSankey(object):

    """
        This class permit to generate latex code directly from the Question
        object.
    """

    def tex(self, other_question):
        """ Return a tikz Sankey Diagram of two questions.

        See this question https://tex.stackexchange.com/questions/40159/
        in order for it to work with your latex file.

        :param Question question: Answers will be left and down
        :param Question other_question: Answers will be right and up """
        sankey = """
\begin{tikzpicture}[x=1pt,y=1pt]

  \begin{sankeydiagram}[
    sankey tot length=90pt,%
    sankey tot quantity=6,%
    sankey min radius=15pt,%
    sankey fill/.style={
      draw,line width=0pt,
      fill,
      lime!50,
    },
    sankey draw/.style={
      draw=black,
      line width=1pt,
      line cap=round,
      line join=round,
    },
    sankey debug,
    ]
    \sankeynodestart{6}{-90}{p0}{0,100};
    \sankeyadvance{p0}{50pt}

    \sankeyfork{p0}{3/p1,3/p2}

    \sankeyturn{p1}{90}
    \sankeyadvance{p1}{20pt}

    \sankeyadvance{p2}{60pt}

    \sankeyfork{p2}{2/p3,1/p4}

    \sankeyturn{p3}{90}
    \sankeyadvance{p3}{50pt}

    \sankeyfork{p3}{1/p5,1/p6}

    \sankeyadvance{p5}{70pt}

    \sankeyfork{p1}{1/p7,1/p8,1/p9}
    \sankeyadvance{p7}{50pt}
    \sankeyadvance{p9}{50pt}

    \sankeyadvance{p4}{40pt}
    \sankeyturn{p4}{90}
    \sankeyadvance{p4}{65pt}

    \sankeyadvance{p7}{40pt}

    \sankeynode{3}{0}{p11}{[shift={(50pt,-15pt)}]p7}
    \sankeyfork{p11}{1/p7a,1/p9a,1/p5a}
    \path (p7) to[sankey flow] (p7a);
    \path (p9) to[sankey flow] (p9a);
    \path (p5) to[sankey flow] (p5a);
    \sankeyadvance{p11}{30pt}
    \sankeynodeend{3}{0}{p11}{p11}

    {
      \tikzset{
        sankey fill/.append style={
          line width=0pt,
          lime!50!green!50,
        }
      }
      \sankeyturn{p8}{-90}
      \sankeyadvance{p8}{40pt}

      \sankeyturn{p6}{-90}
      \sankeyturn{p4}{-90}

      \sankeynode{3}{-90}{p10}{[shift={(-15pt,-60pt)}]p8}
      \sankeyfork{p10}{1/p8a,1/p6a,1/p4a}
      \path (p4) to[sankey flow] (p4a);
      \path (p6) to[sankey flow] (p6a);
      \path (p8) to[sankey flow] (p8a);
      \sankeyadvance{p10}{30pt}
      \sankeynodeend{3}{-90}{p10}{p10}
    }

  \end{sankeydiagram}
\end{tikzpicture}
"""
        return sankey
