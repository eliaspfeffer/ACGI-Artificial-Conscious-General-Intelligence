import numpy as np
from score import getScoreBetweenContexts

#we start with Happiness as the honey pot.

honeypot = ["I am happy"]

#save the position of it into the knowledgetree

knowledgeTree = []
knowledgeTree.append(honeypot[0])

#I have these contexts
contexts = ["smile to be happy. Dont worry be happy."]

#I split the contexts up into single contexts
singleContexts = []
for context in contexts:
    singleContexts.extend(context.split('. '))  # Split at '. ' to keep structure

#I save the single contexts into the knowledge tree
knowledgeTree.extend(singleContexts)


# Check the strength between the context and the honey pot via the score.py

score = getScoreBetweenContexts(honeypot[0], context[0])

# Save the score into the knowledge tree in form of starting context (honey pot), the strength in form of the score and the context.
knowledgeTree.append((honeypot[0], score, context[0]))

#display the knowledge tree in a 3d graph
import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Create data
x = np.array([i for i in range(len(knowledgeTree))])
y = np.array([item[1] for item in knowledgeTree])
z = np.array([0 for _ in range(len(knowledgeTree))])

# Plot data
ax.scatter(x, y, z)

# Label points
for i in range(len(knowledgeTree)):
    ax.text(x[i], y[i], z[i], '%s' % (knowledgeTree[i][0]), size=20, zorder=1, color='k') 

ax.set_xlabel('Context Index')
ax.set_ylabel('Score')
ax.set_zlabel('Z')

plt.show()

#display the knowledge tree in a 3d graph


# focusedContext = [honeypot[0]]

# #the gedankenendlosimpuls is the impulse to think without end.

# #thinking here means jumping from one kontext to another.

# #so it now should have an input. The input here is from wikipedia.
# from getWikipedia import researchAboutThisTopic
# from score import getScoreBetweenContexts
# from mpl_toolkits.mplot3d import Axes3D
# focusedContext = researchAboutThisTopic()