def get_correct_relations(data):
    count = 0
    for d in data:
        relation = d.get('relation').strip()
        predicted_relation = d.get('predicted_relation').strip()
        if relation == predicted_relation:
            count += 1

    return count

def get_partially_correct_relations(data):
    pcr_found = 0
    count = 0
    for d in data:
        relation = d.get('relation').strip()
        predicted_relation = d.get('predicted_relation').strip()
        if relation != predicted_relation and len(predicted_relation) > 0:
            pcr = calculate_partially_correct_relation(relation, predicted_relation)
            count += pcr
            if pcr > 0:
                pcr_found += 1

    print(f'Number of partially correct relations found: {pcr_found}')
    return count

def calculate_partially_correct_relation(relation, predicted_relation):
    split_relation = relation.split(' ')
    split_predict = predicted_relation.split(' ')
    count = 0
    max_len = max(len(split_relation), len(split_predict))
    for word in split_predict:
        if word in split_relation:
            count += 1

    return 0.5 * (count/max_len)


def get_number_of_relations_predicted(data):
    count = 0
    for d in data:
        if d.get('predicted_relation').strip() != '':
            count += 1

    return count

def get_number_of_relations_in_dataset(data):
    return len(data)

def get_exact_precision(data):
    correct_relations = get_correct_relations(data)
    identified_relations = get_number_of_relations_predicted(data)
    return correct_relations/identified_relations

def get_exact_recall(data):
    correct_relations = get_correct_relations(data)
    total_relations = get_number_of_relations_in_dataset(data)
    return correct_relations/total_relations

def get_exact_f_measure(data):
    precision = get_exact_precision(data)
    recall = get_exact_recall(data)
    return (2*precision*recall)/(precision+recall)

def get_partial_precision(data):
    identified_relations = get_number_of_relations_predicted(data)
    correct_relations = get_correct_relations(data)
    partially_correct_relations = get_partially_correct_relations(data)
    return (correct_relations + partially_correct_relations) / identified_relations

def get_partial_recall(data):
    total_relations = get_number_of_relations_in_dataset(data)
    correct_relations = get_correct_relations(data)
    partially_correct_relations = get_partially_correct_relations(data)
    return (correct_relations + partially_correct_relations) / total_relations

def get_partial_f_measure(data):
    precision = get_partial_precision(data)
    recall = get_partial_recall(data)
    return (2*precision*recall)/(precision+recall)