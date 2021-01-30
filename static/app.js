var app = new Vue({
    el: "#app",
    data: {
        input_text: "",
        next_word: "",
    },
    methods: {
        predictNext: function () {
            // check for empty string 
            if (this.input_text.length === 0) {
                console.log("Can't predict on empty text...");
                this.next_word = "Enter something first..."
                return;
            }
            fetch(`/getNext/${this.input_text}/`)
                .then(data => data.json())
                .then(res => {
                    if ("error" in res) {
                        console.log("Error: " + res['error']["message"]);
                    } else {
                        this.next_word = res['nextWord'];
                    }
                });
        }
    },
    watch: {
        input_text: function (newText, oldText) {
            // check for empty string 
            if (newText.length === 0) {
                console.log("Can't predict on empty text...");
                this.next_word = "Enter something first..."
                return;
            }
            fetch(`/getNext/${newText}/`)
                .then(data => data.json())
                .then(res => {
                    if ("error" in res) {
                        console.log("Error: " + res['error']["message"]);
                        this.next_word = res['error']['message'];
                    } else {
                        this.next_word = res['nextWord'];
                    }
                });
        }
    }
});