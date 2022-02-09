def xor(processing_function):
    total_score = 0
    total_score += (1 - processing_function([1,1])[0])
    total_score += (1 - processing_function([0, 0])[0])
    total_score += processing_function([1, 0])[0]
    total_score += processing_function([0, 1])[0]
    return total_score
