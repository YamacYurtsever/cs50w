let counter = 0;
let amount = 10;

document.addEventListener("DOMContentLoaded", loadPosts());

function loadNext() {
	counter += amount;
	document.querySelector("#prev-button").style = "display: inline-block;";
	resetPosts();
	loadPosts();
}

function loadPrev() {
	counter -= amount;
	if (counter < amount) {
		document.querySelector("#prev-button").style = "display: none;";
	}
	resetPosts();
	loadPosts();
}

function loadStart() {
	counter = 0;
	if (document.querySelector("#prev-button")) {
		document.querySelector("#prev-button").style = "display: none;";
	}
	resetPosts();
	loadPosts();
}

function loadThis() {
	resetPosts();
	loadPosts();
}

function resetPosts() {
	document.querySelector("#posts").innerHTML = "";
	document.querySelector("#page-num").innerHTML = counter / amount + 1;
}

function loadPosts() {
	const start = counter;
	const end = counter + amount;

	let fetchURL = "";
	let fetchNextURL = "";

	switch (type) {
		case "all":
			fetchURL = `/load_all_posts?start=${start}&end=${end}`;
			fetchNextURL = `/load_all_posts?start=${end}&end=${end + amount}`;
			break;

		case "profile":
			fetchURL = `/load_profile_posts?start=${start}&end=${end}&username=${username}`;
			fetchNextURL = `/load_profile_posts?start=${end}&end=${end + amount}&username=${username}`;
			break;

		case "following":
			fetchURL = `/load_following_posts?start=${start}&end=${end}`;
			fetchNextURL = `/load_following_posts?start=${end}&end=${end + amount}`;
			break;
	}

	fetch(fetchURL)
		.then((response) => response.json())
		.then((data) => {
			data.posts.forEach(addPost);
		});

	// Open and close next button
	fetch(fetchNextURL)
		.then((response) => response.json())
		.then((data) => {
			if (data.posts.length > 0) {
				document.querySelector("#next-button").style = "display: inline block;";
			} else {
				if (counter == 0) {
					document.querySelector("#page-num").style = "display: none;";
				}
				document.querySelector("#next-button").style = "display: none;";
			}
		});
}

function addPost(post) {
	let newPost = document.createElement("div");
	newPost.className = "post";

	// Format timedate
	const options = {
		day: "2-digit",
		month: "2-digit",
		year: "numeric",
		hour: "2-digit",
		minute: "2-digit",
		second: "2-digit",
		timeZoneName: "short",
	};
	const formattedDate = new Date(post.datetime).toLocaleString("en-GB", options);

	fetch(`/get_username?user_id=${post.user_id}`)
		.then((response) => response.json())
		.then((data) => {
			const username = data.username;

			fetch(`/check_like?post_id=${post.id}`)
				.then((response) => response.json())
				.then((data) => {
					const isLiked = data.isLiked;

					newPost.innerHTML = `
					<h4 class="username"><a href="/profile/${username}">${username}</a></h4>
					${requestUser == post.user_id ? `<p class="edit clickable"><a onclick="edit(this, ${post.id})">Edit</a></p>` : ""}
					<p class="content">${post.content}</p>
					<p class="datetime">${post.edited == true ? "Edited: " : ""} ${formattedDate}</p>
					<p class="likes"><a class="clickable" onclick="toggleLike(${post.id})">${isLiked ? "❤️" : "🤍"}</a>${post.likes}</p> 
					`;
				});
		});

	document.querySelector("#posts").appendChild(newPost);
}

function edit(anchor, postId) {
	const post = anchor.parentElement.parentElement;
	const content = post.querySelector(".content");

	let newForm = document.createElement("form");
	let newTextarea = document.createElement("textarea");
	let newButton = document.createElement("button");

	newTextarea.value = content.innerText;
	newTextarea.rows = 3;
	newButton.innerHTML = "Save";
	newButton.classList.add("post-button");

	newButton.onclick = (event) => {
		updatePost(event, postId, newTextarea.value, content.innerHTML);
		let replaceContent = document.createElement("p");
		replaceContent.classList.add("content");
		replaceContent.innerHTML = newTextarea.value;
		post.replaceChild(replaceContent, newForm);

		let editButton = document.createElement("p");
		editButton.classList.add("edit");
		editButton.innerHTML = `<a onclick="edit(this)">Edit</a>`;
		post.insertBefore(editButton, replaceContent);
	};

	newForm.appendChild(newTextarea);
	newForm.appendChild(newButton);

	post.replaceChild(newForm, content);
	anchor.parentElement.remove();
}

function updatePost(event, postId, newContent, oldContent) {
	event.preventDefault();
	if (newContent != oldContent) {
		fetch("/update_post", {
			method: "POST",
			body: JSON.stringify({
				post_id: postId,
				content: newContent,
			}),
		})
			.then((response) => {
				return response.json();
			})
			.then((result) => {
				console.log(result);
				loadStart();
			});
	} else {
		console.log({ message: "No change made to the post." });
	}
}

function toggleLike(postId) {
	fetch("/toggle_like", {
		method: "POST",
		body: JSON.stringify({
			post_id: postId,
		}),
	})
		.then((response) => {
			return response.json();
		})
		.then((result) => {
			console.log(result);
			loadThis();
		})
		.catch(() => {
			console.log({ error: "User is not authenticated" });
		});
}
