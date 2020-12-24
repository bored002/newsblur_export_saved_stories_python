import time
import api_calls
def test_module():
    print("This is a Test.")
    print("waiting...")
    timer = 30
    while timer>0:
        print('Wait Time left : ' + str(timer))
        time.sleep(10)
        timer-=10        
    print("Done waiting.")
	
if __name__ == "__main__":
	test_module()
 #Place Holder
