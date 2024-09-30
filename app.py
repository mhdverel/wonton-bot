import requests
import json
import time
import random

def get_input(prompt):
    return input(prompt).strip().lower()

def main():
    # Read data from file
    with open('data.txt', 'r') as file:
        queries = [line.strip() for line in file if line.strip()]

    autobuy_shop = get_input("Want to Buy All Kind Shop? (y/n): ")
    claimer = get_input("Want to clear all task? (y/n): ")

    while True:
        for query in queries:
            url = "https://wonton.food/api/v1/user/auth"
            headers = {
                'Content-Type': 'application/json',
                'Accept': '*/*',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 9; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36',
                'X-Requested-With': 'org.telegram.messenger',
                'Origin': 'https://www.wonton.restaurant',
                'Referer': 'https://www.wonton.restaurant/'
            }
            data = {
                'initData': query,
                'inviteCode': '20GB3AB2',
                'newUserPromoteCode': ''
            }

            response = requests.post(url, headers=headers, json=data)
            if response.status_code != 200:
                print('Gagal Login Respons')
                continue

            data = response.json()
            username = data['user']['username']
            token = data['tokens']['accessToken']
            refresh = data['tokens']['refreshToken']
            tiket = data['ticketCount']
            print(f"Berhasil Login Dengan Username {username}")
            print(f"Jumlah Tiket: {tiket}")

            # Check in
            url = "https://wonton.food/api/v1/checkin"
            headers['Authorization'] = f'bearer {token}'
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                print('Curl error:', response.text)
            else:
                data = response.json()
                total_checkin = data['lastCheckinDay']
                print(f"Total Checkin: {total_checkin}")
                print("Getting farming status....")

            # Autobuy shop
            if autobuy_shop == 'y':
                url = "https://wonton.food/api/v1/shop/list"
                response = requests.get(url, headers=headers)

                if response.status_code != 200:
                    print('Error buy items: Received HTTP code', response.status_code)
                else:
                    data = response.json()
                    shop_items = data['shopItems']
                    for shop_item in shop_items:
                        if shop_item['inventory'] <= 1:
                            url = "https://wonton.food/api/v1/shop/use-item"
                            item_data = {'itemId': shop_item['id']}
                            response = requests.post(url, headers=headers, json=item_data)

                            if response.status_code == 200:
                                item_name = shop_item['name']
                                print(f"Succes Buy Items {item_name}")
                            else:
                                print('Error: Received HTTP code', response.status_code)

            # Task claim and verify
            if claimer == 'y':
                url = "https://wonton.food/api/v1/task/list"
                response = requests.get(url, headers=headers)

                if response.status_code == 200:
                    data = response.json()
                    tasks = data['tasks']
                    for task in tasks:
                        task_name = task['name']
                        status_task = task['status']
                        if status_task != 2:
                            # Verify task
                            url = "https://wonton.food/api/v1/task/verify"
                            task_data = {'taskId': task['id']}
                            response = requests.post(url, headers=headers, json=task_data)

                            if response.status_code == 200:
                                print(f"Berhasil Verify task {task_name}")

                            # Claim task
                            url = "https://wonton.food/api/v1/task/claim"
                            response = requests.post(url, headers=headers, json=task_data)

                            if response.status_code == 200:
                                print(f"Berhasil Claim task {task_name}")
                            else:
                                print(f"Gagal Claim Task {task_name}")

            # Check farming status
            url = "https://wonton.food/api/v1/user/farming-status"
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                status_farm = data.get('claimed', False)
                finish_at = data.get('finishAt')
                start_at = data.get('startAt')
                print(f"Start Farming At: {start_at}")
                print(f"status farming {finish_at}")

                if status_farm:
                    print("Trying To Claim Farm..")
                else:
                    print("Claim Not Available/Not Yet start")
                    # Start farming
                    url = 'https://wonton.food/api/v1/user/start-farming'
                    response = requests.post(url, headers=headers, json={})

                    if response.status_code == 200:
                        print('Start Farming Success')
                    else:
                        print('Failed to Start Farming')

            # Start game
            if tiket > 0:
                for _ in range(tiket):
                    url = "https://wonton.food/api/v1/user/start-game"
                    response = requests.post(url, headers=headers)

                    if response.status_code == 200:
                        print("Berhasil Start Game")
                        url = "https://wonton.food/api/v1/user/finish-game"
                        points = random.randint(900, 1000)
                        game_data = {
                            "points": points,
                            "hasBonus": True
                        }
                        response = requests.post(url, headers=headers, json=game_data)

                        if response.status_code == 200:
                            print(f"Berhasil Bermain dengan point {points}")
                        else:
                            print("Gagal Menyelesaikan Game")
                        time.sleep(5)
                    else:
                        print(f"Gagal Start Game: {response.status_code}")
                        time.sleep(2)

        print("SUCCES RUN ALL ACCOUNT SLEEP 1 HOURS")
        time.sleep(3600)

if __name__ == "__main__":
    main()
