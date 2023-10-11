import requests
import os
import glob

# if you encounter a "year is out of range" error the timestamp
# may be in milliseconds, try `ts /= 1000` in that case

baseurl = "https://zerofill-api-qa.unilever.com/"

payload = {}
files = []

images_list = glob.glob("*.png")
print("image_list=>", images_list)
for img in images_list:
    f_name = os.path.basename(img)
    files.append(('files', (f_name, open(f_name, 'rb'), 'image/png')))

headers = {}
print(files)

image_url = baseurl + "uploads/multiple/images/9940257444/0001"
print(image_url)
response = requests.request("POST", image_url, headers=headers, data=payload, files=files)
print(response.text.encode('utf8'))

print("video *********")

video_url = baseurl + "video/all-active-videos"

response = requests.request("GET", video_url, headers=headers, data=payload)

print(response.text)

machine_url = baseurl + "machine/machine-health-status"

payload = 'machineId=zerofill0001&bin1=0.2&bin2=0.9&bin3=0.7%20&cameraHealth=1&status=connected&isCritical=1'
headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
}

response = requests.request("POST", machine_url, headers=headers, data=payload)

print(response.text)
