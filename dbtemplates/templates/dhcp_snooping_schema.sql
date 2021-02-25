CREATE TABLE IF NOT EXISTS dhcp (
    mac text NOT NULL primary key,
    ip text,
    vlan text,
    interface text
);
