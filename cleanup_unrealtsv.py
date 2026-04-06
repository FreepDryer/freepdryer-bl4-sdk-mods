import argparse

filter = [
    'AnimInstance' , 'BlueprintUpdateAnimation', 'Animation', 'CameraModifier'
]


def main():
    parser = argparse.ArgumentParser(
        prog='top'
    )
    parser.add_argument('filename')
    args = parser.parse_args()


    with open(args.filename, "r") as w:
        lines = w.readlines()
    with open('result.tsv', "w") as w:
        for idx, line in enumerate(lines):
            if any(s in line for s in filter):
                continue
            w.write(str(idx) + " "+  line)
    return

if __name__ == "__main__":
    main()