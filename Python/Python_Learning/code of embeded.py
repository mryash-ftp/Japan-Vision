import re

def convert_to_embed_link(url):
    """
    Dailymotion video link ko embed link mein convert karega
    """
    # Remove any whitespace
    url = url.strip()
    
    # Case 1: https://www.dailymotion.com/video/abc123
    pattern1 = r'dailymotion\.com/video/([a-zA-Z0-9]+)'
    match1 = re.search(pattern1, url)
    if match1:
        video_id = match1.group(1)
        return f"https://www.dailymotion.com/embed/video/{video_id}"
    
    # Case 2: https://dai.ly/abc123 (short link)
    pattern2 = r'dai\.ly/([a-zA-Z0-9]+)'
    match2 = re.search(pattern2, url)
    if match2:
        video_id = match2.group(1)
        return f"https://www.dailymotion.com/embed/video/{video_id}"
    
    # Case 3: Already embed link hai
    pattern3 = r'dailymotion\.com/embed/video/([a-zA-Z0-9]+)'
    match3 = re.search(pattern3, url)
    if match3:
        return url  # Already embed link
    
    # If no pattern matches
    return None

def main():
    print("=" * 50)
    print("🎬 Dailymotion Link to Embed Converter")
    print("=" * 50)
    print("\nJitne links doge, main embed links bana dunga.")
    print("'quit' likh kar exit kar sakte ho.\n")
    
    embed_links = []
    
    while True:
        link = input("🔗 Dailymotion link daalo: ").strip()
        
        if link.lower() == 'quit':
            break
        
        if not link:
            print("❌ Kuch daalna toh bhai!\n")
            continue
        
        embed_link = convert_to_embed_link(link)
        
        if embed_link:
            print(f"✅ Embed link: {embed_link}\n")
            embed_links.append(embed_link)
        else:
            print("❌ Ye Dailymotion link nahi lag raha. Dobara try karo.\n")
    
    # Final output
    if embed_links:
        print("\n" + "=" * 50)
        print("📋 Saare embed links (ek line mein):")
        print("=" * 50)
        for i, link in enumerate(embed_links, 1):
            print(f"{i}. {link}")
        
        # Copy-paste ready format for admin panel
        print("\n📝 Admin panel mein daalne ke liye:")
        print("-" * 40)
        for i, link in enumerate(embed_links, 1):
            print(f"Episode {i}: {link}")
    else:
        print("\n⚠️ Koi link save nahi hua.")

if __name__ == "__main__":
    main()