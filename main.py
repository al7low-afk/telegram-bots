import subprocess

def main():
    p1 = subprocess.Popen(["python", "tiktok_bot.py"])
    p2 = subprocess.Popen(["python", "azkar_bot.py"])
    p1.wait()
    p2.wait()

if __name__ == "__main__":
    main()
