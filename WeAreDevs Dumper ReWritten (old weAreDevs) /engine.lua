local runner = {
    ver = "3.1.0",
    max_ops = 8
}

function runner:init()
    self.log = {}
    self.stack = {}
    self.objs = {}
    self.calls = 0
    self.t0 = os.clock()
end

function runner:push(ev, data)
    local e = {
        ts = os.clock() - self.t0,
        ev = ev,
        data = data
    }
    table.insert(self.log, e)
    return e
end

function runner:wrap(name, props)
    local raw = props or {}
    local mt = {}

    mt.__index = function(t, k)
        self:push("get", {obj = name, key = k})
        if raw[k] then return raw[k] end
        return self:wrap(k, {})
    end

    mt.__newindex = function(t, k, v)
        self:push("set", {obj = name, key = k, vtype = type(v)})
        rawset(raw, k, v)
    end

    mt.__tostring = function()
        return "<obj:" .. name .. ">"
    end

    return setmetatable({}, mt)
end

function runner:vec3()
    local v = {}

    function v.new(x, y, z)
        return {
            x = x or 0,
            y = y or 0,
            z = z or 0,
            mag = math.sqrt((x or 0)^2 + (y or 0)^2 + (z or 0)^2)
        }
    end

    function v.add(a, b)
        return v.new(a.x + b.x, a.y + b.y, a.z + b.z)
    end

    function v.dot(a, b)
        return a.x * b.x + a.y * b.y + a.z * b.z
    end

    return v
end

function runner:rbx_api()
    local api = {}

    api.Game = self:wrap("Game", {
        Workspace = self:wrap("Workspace"),
        Players = self:wrap("Players"),
        Lighting = self:wrap("Lighting")
    })

    api.Instances = {}

    function api.Instances.new(cls)
        local inst = self:wrap(cls, {
            Name = cls,
            Parent = nil,
            Destroy = function()
                self:push("destroy", {cls = cls})
            end
        })

        local defaults = {
            Part = {Size = Vector3.new(1, 1, 1), BrickColor = BrickColor.new("Bright green")},
            Script = {Source = "", Disabled = false},
            Humanoid = {Health = 100, WalkSpeed = 16}
        }

        if defaults[cls] then
            for k, v in pairs(defaults[cls]) do
                inst[k] = v
            end
        end

        return inst
    end

    return api
end

function runner:run(code, limit)
    limit = limit or self.max_ops
    local ok, res = pcall(function()
        local env = {}

        setmetatable(env, {
            __index = function(t, k)
                if k == "game" then
                    return self:rbx_api().Game
                elseif k == "Vector3" then
                    return self:vec3()
                elseif k == "print" then
                    return function(...)
                        self:push("print", {...})
                    end
                end
                return nil
            end
        })

        local fn, err = loadstring(code)
        if not fn then
            error("compile error: " .. tostring(err))
        end

        setfenv(fn, env)

        local hook = function()
            if os.clock() - self.t0 > limit then
                error("timeout")
            end
        end

        debug.sethook(hook, "", 10000)
        local out = {fn()}
        debug.sethook()

        return out
    end)

    return ok, res, self.log
end

return runner
