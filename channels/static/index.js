function Like(post_id) {
    const likeCount = document.getElementById(`likes-count-${post_id}`);
    const likebutton = document.getElementById(`like-button-${post_id}`);
    fetch(`/admin/channels/like/${post_id}`, { method:"POST" }).then((res) => res.json()).then((data) => {
        likeCount.innerHTML = data["likes"];
        if (data["liked"]) {
            likebutton.className = "fa-solid fa-heart";
        } else {
            likebutton.className = "fa-regular fa-heart";
        }
    });
}