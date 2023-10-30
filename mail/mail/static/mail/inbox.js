document.addEventListener("DOMContentLoaded", function () {
	// Get the email template
	const emailTemplate = document.querySelector(".email");

	// Use buttons to toggle between views
	document.querySelector("#inbox").addEventListener("click", () => load_mailbox("inbox", emailTemplate));
	document.querySelector("#sent").addEventListener("click", () => load_mailbox("sent", emailTemplate));
	document.querySelector("#archived").addEventListener("click", () => load_mailbox("archive", emailTemplate));
	document.querySelector("#compose").addEventListener("click", () => compose_email());

	// By default, load the inbox
	load_mailbox("inbox", emailTemplate);
});

function compose_email(recipients = "", subject = "", body = "", timestamp = "") {
	// Show compose view and hide other views
	document.querySelector("#compose-view").style.display = "block";
	document.querySelector("#emails-view").style.display = "none";
	document.querySelector("#email-view").style.display = "none";

	// Clear or prefill email
	document.querySelector("#compose-recipients").value = recipients;
	document.querySelector("#compose-subject").value = subject;
	document.querySelector("#compose-body").value = body;

	// Format prefill
	if (subject != "" && subject.substring(0, 3) != "Re:") {
		document.querySelector("#compose-subject").value = "Re: " + subject;
	}
	if (body != "") {
		document.querySelector("#compose-body").value = `\n\nOn ${timestamp} ${recipients} wrote: \n\t${body}`;
	}

	// Send email
	const form = document.querySelector("#compose-form");
	form.onsubmit = () => {
		fetch("/emails", {
			method: "POST",
			body: JSON.stringify({
				recipients: document.querySelector("#compose-recipients").value,
				subject: document.querySelector("#compose-subject").value,
				body: document.querySelector("#compose-body").value,
			}),
		})
			.then((response) => {
				if (response.status === 201) {
					load_mailbox("sent");
				}
				return response.json();
			})
			.then((result) => {
				// Print result
				console.log(result);
			});
		return false;
	};
}

function load_mailbox(mailbox, emailTemplate) {
	// Show the mailbox and hide other views
	document.querySelector("#emails-view").style.display = "block";
	document.querySelector("#compose-view").style.display = "none";
	document.querySelector("#email-view").style.display = "none";

	// Show the mailbox name
	document.querySelector("#emails-view").innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

	// Display mailbox
	fetch(`/emails/${mailbox}`)
		.then((response) => response.json())
		.then((emails) => {
			// Show the emails
			emails.forEach((email) => {
				newEmail = emailTemplate.cloneNode(true);
				newEmail.querySelector(".id").innerHTML = email.id;
				newEmail.querySelector(".sender").innerHTML = email.sender;
				newEmail.querySelector(".subject").innerHTML = email.subject;
				newEmail.querySelector(".timestamp").innerHTML = email.timestamp;
				if (email.read === true) {
					newEmail.style.backgroundColor = "gray";
				}
				document.querySelector("#emails-view").appendChild(newEmail);
			});

			// Opening Emails
			open_emails(emailTemplate);
		});
}

function open_emails(emailTemplate) {
	emails = document.querySelectorAll(".email");
	emails.forEach((email) => {
		email.addEventListener("click", () => {
			id = email.querySelector(".id").innerHTML;
			fetch(`/emails/${id}`)
				.then((response) => response.json())
				.then((email) => {
					// Fill email contents
					document.querySelector("#email-view").innerHTML = `
						<h1>${email.subject}</h1>
						<p><em>Sender:</em> ${email.sender}</p>
						<p><em>Recipients:</em> ${email.recipients}</p>
						<p>${email.body.replace(/\n/g, "<br>").replace(/\t/g, "&emsp;")}</p>
						<p>${email.timestamp}</p>
					`;

					// Handle the archive button
					const archiveButton = document.createElement("button");
					let willArchive;
					if (email.archived == false) {
						archiveButton.textContent = "Archive";
						willArchive = true;
					} else {
						archiveButton.textContent = "Unarchive";
						willArchive = false;
					}
					archiveButton.addEventListener("click", () => {
						fetch(`/emails/${id}`, {
							method: "PUT",
							body: JSON.stringify({
								archived: willArchive,
							}),
						}).then(() => {
							load_mailbox("inbox", emailTemplate);
						});
					});
					document.querySelector("#email-view").appendChild(archiveButton);

					// Handle Reply Button
					if (email.recipients.includes(myEmail)) {
						const replyButton = document.createElement("button");
						replyButton.textContent = "Reply";
						replyButton.addEventListener("click", () => {
							compose_email((recipients = email.sender), (subject = email.subject), (body = email.body), (timestamp = email.timestamp));
						});
						document.querySelector("#email-view").appendChild(replyButton);
					}

					// Mark as read
					fetch(`/emails/${id}`, {
						method: "PUT",
						body: JSON.stringify({
							read: true,
						}),
					});

					// Show email view and hide other views
					document.querySelector("#email-view").style.display = "block";
					document.querySelector("#emails-view").style.display = "none";
					document.querySelector("#compose-view").style.display = "none";
				});
		});
	});
}
