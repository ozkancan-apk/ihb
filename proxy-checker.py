from rich.progress import Progress
import multiprocessing
import requests
import concurrent.futures

# Adım 1
with open('proxy.txt', 'r') as file:
    proxies = file.readlines()
    chunk_size = len(proxies) // 5
    divided_proxies = [proxies[i:i + chunk_size] for i in range(0, len(proxies), chunk_size)]

    for i, proxy_list in enumerate(divided_proxies, start=1):
        with open(f'{i}.txt', 'w') as f:
            f.writelines(proxy_list)

# Adım 2
alan1 = divided_proxies[0]
alan2 = divided_proxies[1]
alan3 = divided_proxies[2]
alan4 = divided_proxies[3]
alan5 = divided_proxies[4]

# Adım 3
cekirdek1 = alan1
cekirdek2 = alan2
cekirdek3 = alan3
cekirdek4 = alan4
cekirdek5 = alan5

# Adım 4
with Progress() as progress:
    task1 = progress.add_task("[red]İşlem 1...", total=len(cekirdek1))
    task2 = progress.add_task("[green]İşlem 2...", total=len(cekirdek2))
    task3 = progress.add_task("[blue]İşlem 3...", total=len(cekirdek3))
    task4 = progress.add_task("[cyan]İşlem 4...", total=len(cekirdek4))
    task5 = progress.add_task("[magenta]İşlem 5...", total=len(cekirdek5))

    def update_progress(task, proxies):
        for proxy in proxies:
            url = 'https://www.instagram.com/'
            proxy_stripped = proxy.strip()
            proxies = {
                'http': f'http://{proxy_stripped}',
                'https': f'https://{proxy_stripped}'
            }
            try:
                response = requests.get(url, proxies=proxies, timeout=1)
                if response.status_code == 200:
                    with open('clean.txt', 'a') as clean_file:
                        clean_file.write(proxy)
            except:
                pass
            progress.update(task, advance=1)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.submit(update_progress, task1, cekirdek1)
        executor.submit(update_progress, task2, cekirdek2)
        executor.submit(update_progress, task3, cekirdek3)
        executor.submit(update_progress, task4, cekirdek4)
        executor.submit(update_progress, task5, cekirdek5)

# Adım 6, 7, 8
# Gerekli işlemleri buraya ekleyin

# Adım 9
# Kodun doğru çalıştığından emin olun
