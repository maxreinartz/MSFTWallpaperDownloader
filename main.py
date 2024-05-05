import aiohttp
import asyncio
import time
import os

startTime = time.time()

async def download_wallpaper(session, url, filename):
    os.makedirs("wallpapers", exist_ok=True)
    async with session.get(url) as response:
        content = await response.read()
        with open(os.path.join("wallpapers", filename), "wb") as file:
            file.write(content)
    print(f"Downloaded {filename}")

async def main():
    print("Using wallpaperhub to download the Microsoft wallpapers")
    pages = input("Enter the number of pages to download (1 page is 20 wallpapers | -1 is all): ")
    if pages == "":
        pages = 1
    elif int(pages) < 1:
        url = "https://wallpaperhub.app/api/v1/creators/microsoft/wallpapers"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                pages = data["totalPages"]
                print(f"Downloading all {pages} pages...")

    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(1, int(pages) + 1):
            url = f"https://wallpaperhub.app/api/v1/creators/microsoft/wallpapers?page={i}"
            async with session.get(url) as response:
                data = await response.json()
                print(f"Preparing downloads for page {i} of {pages}")

                for wallpaper in data["entities"]:
                    for variation in wallpaper["entity"]["variations"]:
                        wallpaper_url = variation["resolutions"][0]["url"]
                        wallpaper_id = wallpaper["entity"]["id"]
                        filename = wallpaper["entity"]["title"].translate(str.maketrans("", "", r'\/:*?"<>|')).replace(" ", "_") + " (" + wallpaper_id + ").jpg"
                        if not os.path.exists(os.path.join("wallpapers", filename)):
                            task = asyncio.create_task(download_wallpaper(session, wallpaper_url, filename))
                            tasks.append(task)
                            print(f"{data['entities'].index(wallpaper) + 1} of {len(data['entities'])} on page {i} of {pages} | Downloading {filename}")
                        else:
                            print(f"{data['entities'].index(wallpaper) + 1} of {len(data['entities'])} on page {i} of {pages} | Skipped {filename}, already exists.")
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())

print(f"Done downloading wallpapers.\nDownloaded: {len(os.listdir('wallpapers'))}.\nTime elapsed: {time.time() - startTime:.2f}s")