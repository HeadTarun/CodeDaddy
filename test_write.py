from functions.write_file import write_file


def run_tests():
    print('write_file("calculator", "lorem.txt", "...")')
    print(write_file("calculator", "lorem.txt", "wait, this isn't lorem ipsum"))
    print()

    print('write_file("calculator", "pkg/morelorem.txt", "...")')
    print(write_file("calculator", "pkg/morelorem.txt", "lorem ipsum dolor sit amet"))
    print()

    print('write_file("calculator", "/tmp/temp.txt", "...")')
    print(write_file("calculator", "/tmp/temp.txt", "this should not be allowed"))
    print()


if __name__ == "__main__":
    run_tests()