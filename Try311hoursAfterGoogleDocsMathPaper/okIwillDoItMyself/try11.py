#####################Start########################

########## Input: Sentences
sentences = ["I am a sentence. I am another sentence. I am a third sentence."]

#### Single sentence
# Split up the text into individual sentences based on "."
allSentencesSplitUp = []
for singleSentence in sentences:
    allSentencesSplitUp.extend(singleSentence.split('. '))  # Split at '. ' to keep structure

### Clean up
# Remove empty strings caused by splitting
allSentencesSplitUp = [s.strip() for s in allSentencesSplitUp if s]

### Test
print("Split sentences:")
for singleSentence in allSentencesSplitUp:
    print(singleSentence)

#### Matrixes for words
# Initialize an empty matrix for words
woerterMatrix = []
# Save the words in the matrix (if not already saved)
for singleSentence in allSentencesSplitUp:
    woerter = singleSentence.split()  # Split into words
    for wort in woerter:
        if wort not in [reihe[0] for reihe in woerterMatrix]:  # Avoid duplicates
            woerterMatrix.append([wort, 0])  # Initialize count column

### Matrixes for sentences: Contains of the position of words in the words-matrix
# Initialize an empty matrix for sentences
sentencesMatrix = []
# Save the sentences in the matrix
for singleSentence in allSentencesSplitUp:
    woerter = singleSentence.split()            # Split the sentence into words
    sentenceMatrixRow = []                      # Initialize row for sentence
    for wort in woerter:                        # For each word in the sentence
        for i, row in enumerate(woerterMatrix): # Enumerate to get the position of the word in the words-matrix
            if row[0] == wort:                  # Find the word in the words-matrix (row[0] is the word)
                sentenceMatrixRow.append(i)     # Save the position of the word in the words-matrix
    sentencesMatrix.append(sentenceMatrixRow)   # Save the row in the sentences-matrix

### print sentencesMatrix
print("\nMatrix for sentences:")
for row in sentencesMatrix:
    print(row)


### Utter trash. Dont need that. Word connection strength to matrix is always 1. Dont need Matrix with that.
# Increment the count for each word found in sentences
for singleSentence in allSentencesSplitUp:
    woerter = singleSentence.split()  # Split into words
    for wort in woerter:
        for row in woerterMatrix:
            if row[0] == wort:
                row[1] += 1  # Increment count

#matrix for 
# Print matrix
print("\nAfter counting words in sentences:")
for row in woerterMatrix:
    print(row)


#####################End########################