import csv
import os

class myDB:
    def __init__(self, file_path):
        self.file_path = file_path

        # check if correct file headers are present
        if os.path.exists(file_path):
            with open(file_path, mode='r') as file:
                reader = csv.reader(file)
                headers = next(reader)
                if headers != ['id', 'data']:
                    raise ValueError(f'Invalid file headers: {headers}')

        # Create file if it doesn't exist
        if not os.path.exists(file_path):
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['id', 'data'])  # Initialize with header
        
    
    def new_entry(self, data):
        with open(self.file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([self._get_next_id(), data])


    def select_all(self):
        with open(self.file_path, mode='r') as file:
            reader = csv.DictReader(file)
            return list(reader)

    def select_by_id(self, record_id):
        with open(self.file_path, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['id'] == str(record_id):
                    return row
        return None

    def update(self, record_id, new_data):
        records = self.select_all()
        record_found = False
        with open(self.file_path, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['id', 'data'])
            writer.writeheader()
            for row in records:
                if row['id'] == str(record_id):
                    row['data'] = new_data
                    record_found = True
                writer.writerow(row)
    
        if not record_found:
            raise ValueError(f"Record with id {record_id} does not exist.")

    def delete(self, record_id):
        self.update(record_id, None)

    def nuke_db(self):
        with open(self.file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['id', 'data'])

    def _get_next_id(self):
        records = self.select_all()
        return int(records[-1]['id']) + 1 if records else 1

if __name__ == '__main__':
    db = myDB('db.csv')
    db.nuke_db()
    db.new_entry('this is the first data')
    print(db.select_all())
    print(db._get_next_id())
    db.new_entry('this is the second data')
    print(db.select_all())
    print(db._get_next_id())
    db.delete(1)
    print(db.select_all())