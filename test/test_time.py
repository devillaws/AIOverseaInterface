import time

start_time = time.time()
print("开始时间", start_time)
time.sleep(5)#延迟5秒
end_time = time.time()
print("结束时间", end_time)
dec_time = end_time - start_time
print("相差时间", dec_time)
if dec_time < 3:
    print("时间小于3秒")
else:
    print("时间大于3秒")