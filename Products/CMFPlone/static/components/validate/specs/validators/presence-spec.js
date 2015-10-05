describe('validator.presence', function() {
  var presence = validate.validators.presence.bind(validate.validators.presence);

  afterEach(function() {
    delete validate.validators.presence.message;
    delete validate.validators.presence.options;
  });

  it("doesn't allow empty values", function() {
    expect(presence('', {})).toBeDefined();
    expect(presence('  ', {})).toBeDefined();
    expect(presence(null, {})).toBeDefined();
    expect(presence(undefined, {})).toBeDefined();
    expect(presence([], {})).toBeDefined();
    expect(presence({}, {})).toBeDefined();
  });

  it("allows non empty values", function() {
    expect(presence('foo', {})).not.toBeDefined();
    expect(presence(0, {})).not.toBeDefined();
    expect(presence(false, {})).not.toBeDefined();
    expect(presence([null], {})).not.toBeDefined();
    expect(presence({foo: null}, {})).not.toBeDefined();
    expect(presence(function(){return null;}, {})).not.toBeDefined();
  });

  it("has a nice default message", function() {
    var msg = presence(null, {});
    expect(msg).toEqual("can't be blank");
  });

  it("also allows to specify your own nice message", function() {
    validate.validators.presence.message = "default message";
    expect(presence(null, {})).toEqual("default message");
    expect(presence(null, {message: "my message"})).toEqual("my message");
  });

  it("supports default options", function() {
    validate.validators.presence.options = {message: "barfoo"};
    var options = {message: 'foobar'};
    expect(presence(null, options)).toEqual('foobar');
    expect(presence(null, {})).toEqual('barfoo');
    expect(validate.validators.presence.options).toEqual({message: "barfoo"});
    expect(options).toEqual({message: "foobar"});
  });
});
