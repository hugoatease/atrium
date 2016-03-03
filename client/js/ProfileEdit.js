var React = require('react');
var request = require('superagent');
var ReactQuill = require('react-quill');
var ReactDOM = require('react-dom');
var Dropzone = require('react-dropzone');

var ProfileEdit = React.createClass({
    getInitialState: function() {
        return {
            first_name: null,
            last_name: null,
            photo: null,
            facebook_id: null,
            twitter_id: null,
            biography: null,
            uploading: false
        }
    },

    componentDidMount: function() {
        request.get('/api/profiles/' + this.props.params.id)
            .end(function(err, res) {
                if (err) return;
                this.setState(res.body);
            }.bind(this));
    },

    bioChange: function(text) {
        this.setState({biography: text});
    },

    facebookChange: function(ev) {
        this.setState({facebook_id: ev.target.value});
    },

    twitterChange: function(ev) {
        this.setState({twitter_id: ev.target.value});
    },

    update: function(ev) {
        ev.preventDefault();
        request.put('/api/profiles/me')
            .send({
                facebook_id: this.state.facebook_id,
                twitter_id: this.state.twitter_id,
                biography: this.state.biography
            })
            .end(function(err, res) {
                if (err) return;
                this.setState(res.body);
            }.bind(this));
    },

    uploadPhoto: function(file) {
        this.setState({uploading: true});
        request.post('/api/profiles/me/photo')
            .attach('photo', file[0])
            .end(function(err, res) {
                if (err) return;
                this.setState({uploading: false});
                this.setState(res.body);
            }.bind(this));
    },

    render: function() {
        if (!this.state.photo) {
            var photo = (
                <Dropzone multiple={false} onDrop={this.uploadPhoto}>
                    {!this.state.uploading ? <span>
                        Drop your photo or click to select file.
                    </span> : <span>Uploading photo...</span>}
                </Dropzone>
            );
        }
        else {
            var photo = (
                <div>
                    <img src={this.state.photo} />
                </div>
            )
        }

        return (
            <div className="row">
                <form onSubmit={this.update}>
                    <div className="medium-4 column">
                        <h5>{this.state.first_name} {this.state.last_name}</h5><hr />
                        {photo}
                        <label>
                            <span>Facebook ID</span>
                            <input type="text" placeholder="Facebook ID" value={this.state.facebook_id} ref="facebook_id" onChange={this.facebookChange} />
                        </label>
                        <label>
                            <span>Twitter ID</span>
                            <input type="text" placeholder="Twitter ID" value={this.state.twitter_id} ref="twitter_id" onChange={this.twitterChange} />
                        </label>
                        <button type="submit" className="button success">Save</button>
                    </div>
                    <div className="medium-8 column">
                        <h5>Biography</h5><hr />
                        <ReactQuill placeholder="Biography" value={this.state.biography} theme="snow" ref="biography" onChange={this.bioChange} />
                    </div>
                </form>
            </div>
        );
    }
});

module.exports = ProfileEdit;