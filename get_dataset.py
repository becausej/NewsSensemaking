# from https://huggingface.co/datasets/ucsbnlp/liar
import datasets

# Load the dataset
def load_data():
    dataset = datasets.load_dataset('liar')
    
    train_data = dataset['train']
    test_data = dataset['test']
    validation_data = dataset['validation']
    return train_data, test_data, validation_data

# We need to remap the labels to an actual scale that is ordered
def remap_labels(labels):
    # Labels:
    # 0: false
    # 1: half-True
    # 2: mostly-True
    # 3: true
    # 4: barely-True
    # 5: pants-Fire
    remap_dict = {3: 5, 2: 4, 1: 3, 4: 2, 0: 1, 5: 0}
    return [remap_dict[label] for label in labels]

# We only care about statement and label
def get_data(data):
    statement = data['statement']
    label = data['label']
    label = remap_labels(label)
    return statement, label

def get_and_preprocess_data():
    train_data, test_data, validation_data = load_data()

    train_statement, train_label = get_data(train_data)
    test_statement, test_label = get_data(test_data)
    validation_statement, validation_label = get_data(validation_data)
    
    # now convert labels to 0 - 1 scale
    train_label = [label / 5 for label in train_label]
    test_label = [label / 5 for label in test_label]
    validation_label = [label / 5 for label in validation_label]
    
    return train_statement, train_label, test_statement, test_label, validation_statement, validation_label
